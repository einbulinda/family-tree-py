from typing import List, Set, Sequence, Dict, Optional, Callable

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, select

from app.models.individual import Individual
from app.models.relationship import Relationship
from app.schemas.tree_schema import ImmediateFamily, MultiLevelTree, GenerationBand
from app.schemas.individual_schema import IndividualResponse


class TreeService:

    # ----------------------- LOW LEVEL HELPERS ---------------------------------- #

    @staticmethod
    def _get_individual(db:Session, individual_id:int)-> Optional[Individual]:
        stmt = select(Individual).where(Individual.id == individual_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def _get_all_relationships_for(db: Session, individual_id: int) -> Sequence[Relationship]:
        """
        Fetch all relationships where this individual appears on either side.
        """
        stmt = select(Relationship).where(
            or_(
                Relationship.individual_id == individual_id,
                Relationship.related_individual_id == individual_id,
            )
        )

        result = db.execute(stmt)
        return result.scalars().all()


    @staticmethod
    def _classify_direct_relations(
            individual_id: int, rels: List[Relationship]
    ) -> tuple[Set[int], Set[int], Set[int]]:
        """
        From a list of Relationship rows involving `individual_id`,
        classify parent_ids, child_ids, spouse_ids.

        Note: because a relationship can be stored as either:
          - parent (parent -> child)
          - child  (child  -> parent)
        we interpret direction based on both relationship_type AND which side
        the current individual is on.
        """
        parent_ids: Set[int] = set()
        child_ids: Set[int] = set()
        spouse_ids: Set[int] = set()

        for rel in rels:
            # Determine "other" side
            if rel.individual_id == individual_id:
                other_id = rel.related_individual_id
                side = "left"  # current individual is `individual_id` field
            else:
                other_id = rel.individual_id
                side = "right"  # current individual is `related_individual_id` field

            if rel.relationship_type == "spouse":
                spouse_ids.add(other_id)

            elif rel.relationship_type == "parent":
                # parent -> child
                if side == "left":
                    # current = parent, other = child
                    child_ids.add(other_id)
                else:
                    # current = child, other = parent
                    parent_ids.add(other_id)

            elif rel.relationship_type == "child":
                # child -> parent (inverse of above)
                if side == "left":
                    # current = child, other = parent
                    parent_ids.add(other_id)
                else:
                    # current = parent, other = child
                    child_ids.add(other_id)


        return parent_ids, child_ids, spouse_ids

    # ---------- helpers that return *ID sets* (not Relationship objects) -----

    @staticmethod
    def _get_children_of_parent(db: Session, parent_id: int) -> Set[int]:
        """
        Get all children of a parent from Relationship table.
        We consider both representations: 'parent' and 'child'.
        """

        # Case 1: (parent)-[parent]->(child)
        stmt1 = select(Relationship.related_individual_id).where(
            and_(
                Relationship.individual_id == parent_id,
                Relationship.relationship_type == "parent",
            )
        )

        stmt2 = select(Relationship.individual_id).where(
            and_(
                Relationship.related_individual_id == parent_id,
                Relationship.relationship_type == "child",
            )
        )

        ids1 = db.execute(stmt1).scalars().all()
        ids2 = db.execute(stmt2).scalars().all()

        return set(ids1) | set(ids2)

    @staticmethod
    def _get_parents_of_child(db:Session, child_id: int) ->Set[int]:
        """
        Get all parents of a child from Relationship table
        Symmetric to _get_children_of_parent
        """

        # Case 1: relationship_type = 'parent', child is right side
        stmt1 = select(Relationship.individual_id).where(
            and_(
                Relationship.related_individual_id == child_id,
                Relationship.relationship_type == "parent"
            )
        )

        # Case 2: relationship_type='child', child is left side
        stmt2 = select(Relationship.related_individual_id).where(
            and_(
                Relationship.individual_id == child_id,
                Relationship.relationship_type == "child",
            )
        )

        ids1 = db.execute(stmt1).scalars().all()
        ids2 = db.execute(stmt2).scalars().all()

        return set(ids1) | set(ids2)


    # ----------------------- SCHEMA MAPPING ------------------------------ #

    @staticmethod
    def to_schema(individual: Individual) -> IndividualResponse:
        """
        Convert ORM Individual -> Pydantic IndividualResponse explicitly.
        """
        return IndividualResponse.model_validate(individual)


    # ----------------------- IMMEDIATE /  SMART TREE ------------------------------------- #

    @staticmethod
    def build_immediate_family(db: Session, individual_id: int) -> ImmediateFamily | None:
        """
        Smart/immediate tree:
        - root
        - parents
        - siblings  (based on shared parents)
        - spouses
        - children
        """
        root = TreeService._get_individual(db, individual_id)
        if not root:
            return None

        # Get all relationship edges (two-sided)
        rels = TreeService._get_all_relationships_for(db, individual_id)
        parent_ids, child_ids, spouse_ids = TreeService._classify_direct_relations(
            individual_id, rels
        )

        # ------------------- FIND SIBLINGS ---------------------------------- #

        sibling_ids: Set[int] = set()
        for parent_id in parent_ids:
            all_children = TreeService._get_children_of_parent(db, parent_id)
            for cid in all_children:
                if cid != individual_id:
                    sibling_ids.add(cid)

        # ------------------- QUERY ACTUAL INDIVIDUALS ------------------------ #

        # Fetch all individuals for each group
        def fetch_many(ids: Set[int])->Sequence[Individual]:
            if not ids:
                return []
            stmt = select(Individual).where(Individual.id.in_(ids))
            result = db.execute(stmt)
            return result.scalars().all()

        parents = fetch_many(parent_ids)
        spouses = fetch_many(spouse_ids)
        children = fetch_many(child_ids)
        siblings = fetch_many(sibling_ids)

        # ------------------- RETURN SCHEMA ----------------------------------- #

        return ImmediateFamily(
            root=TreeService.to_schema(root),
            parents=[TreeService.to_schema(p) for p in parents],
            siblings=[TreeService.to_schema(s) for s in siblings],
            spouses=[TreeService.to_schema(s) for s in spouses],
            children=[TreeService.to_schema(c) for c in children],
        )

    # ---------- multi-level ancestors / descendants ----------

    @staticmethod
    def _bfs_generations(
            db: Session,
            start_ids: Set[int],
            step_func: Callable[[Session, int], Set[int]],
            initial_generation: int,
            step: int,
            max_depth: int,
            seen: Set[int],
    ) -> Dict[int, Set[int]]:
        """
        Generic BFS used for both ancestors and descendants.

        step_func: given person_id -> set[related_id]
        initial_generation: usually 0 (root)
        step: +1 for descendants, -1 for ancestors
        """
        generations: Dict[int, Set[int]] = {}
        current_ids = set(start_ids)
        current_generation = initial_generation

        for _ in range(max_depth):
            if not current_ids:
                break

            next_ids: Set[int] = set()
            for pid in current_ids:
                related_ids = step_func(db, pid)
                for rid in related_ids:
                    if rid not in seen:
                        seen.add(rid)
                        next_ids.add(rid)

            if not next_ids:
                break

            current_generation += step
            generations[current_generation] = next_ids
            current_ids = next_ids

        return generations

    @staticmethod
    def build_multi_level_tree(
        db: Session,
        individual_id: int,
        direction: str = "both",
        max_depth: int = 3,
    ) -> MultiLevelTree | None:
        """
        Build a multi-level tree in ancestor/descendant or both directions.

        direction: "ancestors", "descendants", or "both"
        max_depth: how many generations up/down to explore.
        """
        root = TreeService._get_individual(db, individual_id)
        if not root:
            return None

        seen: Set[int] = {individual_id}
        generations: Dict[int, Set[int]] = {0: {individual_id}}

        # Ancestors: negative generations
        if direction in ("ancestors", "both"):
            ancestor_gens = TreeService._bfs_generations(
                db=db,
                start_ids={individual_id},
                step_func=TreeService._get_parents_of_child,
                initial_generation=0,
                step=-1,
                max_depth=max_depth,
                seen=seen,
            )
            generations.update(ancestor_gens)

        # Descendants: positive generations
        if direction in ("descendants", "both"):
            descendant_gens = TreeService._bfs_generations(
                db=db,
                start_ids={individual_id},
                step_func=TreeService._get_children_of_parent,
                initial_generation=0,
                step=+1,
                max_depth=max_depth,
                seen=seen,
            )
            generations.update(descendant_gens)

        # Materialize ORM -> schemas
        bands: List[GenerationBand] = []
        for gen_index in sorted(generations.keys()):
            ids = generations[gen_index]
            if ids:
                stmt = select(Individual).where(Individual.id.in_(ids))
                result = db.execute(stmt)
                individuals = result.scalars().all()
            else:
                individuals = []

            bands.append(
                GenerationBand(
                    generation=gen_index,
                    individuals=[TreeService.to_schema(ind) for ind in individuals],
                )
            )

        return MultiLevelTree(
            root=TreeService.to_schema(root),
            generations=bands,
        )