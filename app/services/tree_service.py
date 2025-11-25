from typing import List, Set, Sequence, Dict

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, select

from app.models.individual import Individual
from app.models.relationship import Relationship
from app.schemas.tree_schema import ImmediateFamily, MultiLevelTree, GenerationBand
from app.schemas.individual_schema import IndividualResponse


class TreeService:

    # ----------------------- LOW LEVEL HELPERS ---------------------------------- #

    @staticmethod
    def _get_individual(db:Session, individual_id:int)-> Individual | None:
        return db.query(Individual).filter(Individual.id == individual_id).first()

    @staticmethod
    def _get_all_relationships_for(db: Session, individual_id: int) -> List[Relationship]:
        """
        Fetch all relationships where this individual appears on either side.
        """
        return (
            db.query(Relationship)
            .filter(
                or_(
                    Relationship.individual_id == individual_id,
                    Relationship.related_individual_id == individual_id,
                )
            )
            .all()
        )

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

    @staticmethod
    def _get_children_of_parent(db: Session, parent_id: int) -> Set[int]:
        """
        Get all children of a parent from Relationship table.
        We consider both representations: 'parent' and 'child'.
        """
        children: Set[int] = set()

        # Case 1: relationship_type='parent', parent_id is left side
        parent_rels = (
            db.query(Relationship)
            .filter(
                and_(
                    Relationship.individual_id == parent_id,
                    Relationship.relationship_type == "parent",
                )
            )
            .all()
        )
        for rel in parent_rels:
            children.add(rel.related_individual_id)

        # Case B — stored as (child -> parent)
        rels_child = (
            db.query(Relationship)
            .filter(
                and_(
                    Relationship.related_individual_id == parent_id,
                    Relationship.relationship_type == "child",
                )
            )
            .all()
        )
        for rel in rels_child:
            children.add(rel.individual_id)

        return children

    @staticmethod
    def _get_parents_of_child(db:Session, child_id: int) ->Set[int]:
        """
        Get all parents of a child from Relationship table
        Symmetric to _get_children_of_parent
        """
        parents : Set[int] = set()

        # Case 1: relationship_type = 'parent', child is right side
        parent_rels =(
            db.query(Relationship).filter(
                and_(
                    Relationship.related_individual_id == child_id,
                    Relationship.relationship_type == "parent"
                )
            ).all()
        )
        for rel in parent_rels:
            parents.add(rel.individual_id)

        # Case 2: relationship_type='child', child is left side
        child_rels = (
            db.query(Relationship)
            .filter(
                and_(
                    Relationship.individual_id == child_id,
                    Relationship.relationship_type == "child",
                )
            )
            .all()
        )
        for rel in child_rels:
            parents.add(rel.related_individual_id)

        return parents

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
        for p in parent_ids:
            all_children = TreeService._get_children_of_parent(db, p)
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
        step_func,
        start_generation: int,
        max_depth: int,
        seen: Set[int],
    ) -> Dict[int, Set[int]]:
        """
        Generic BFS across generations using a step function.

        step_func: given an individual_id -> returns a set of related ids
                   (e.g., parents or children).
        """
        generations: Dict[int, Set[int]] = {}
        current_gen_ids = set(start_ids)
        current_generation = start_generation

        depth = 0
        while current_gen_ids and depth < max_depth:
            # collect next frontier
            next_ids: Set[int] = set()
            for iid in current_gen_ids:
                related_ids = step_func(db, iid)
                for rid in related_ids:
                    if rid not in seen:
                        seen.add(rid)
                        next_ids.add(rid)

            if not next_ids:
                break

            # move one generation step
            current_generation = current_generation + 1 if start_generation >= 0 else current_generation - 1
            generations[current_generation] = next_ids
            current_gen_ids = next_ids
            depth += 1

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
                start_generation=0,
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
                start_generation=0,
                max_depth=max_depth,
                seen=seen,
            )
            generations.update(descendant_gens)

        # Materialize ORM -> schemas
        bands: List[GenerationBand] = []
        for gen_index in sorted(generations.keys()):
            ids = generations[gen_index]
            individuals = (
                db.query(Individual).filter(Individual.id.in_(ids)).all() if ids else []
            )
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