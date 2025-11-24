from typing import List, Set

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.individual import Individual
from app.models.relationship import Relationship
from app.schemas.tree_schema import ImmediateFamily
from app.schemas.individual_schema import IndividualResponse


class TreeService:

    # ----------------------- CORE HELPERS ---------------------------------- #

    @staticmethod
    def _get_root(db:Session, individual_id:int)-> Individual | None:
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

    # ----------------------- SCHEMA CONVERSION ------------------------------ #

    @staticmethod
    def to_schema(individual: Individual) -> IndividualResponse:
        return IndividualResponse.model_validate(individual)

    # ----------------------- BUILD TREE ------------------------------------- #

    @staticmethod
    def build_immediate_family(db: Session, individual_id: int) -> ImmediateFamily | None:
        """
        Smart family tree: returns parents, siblings, spouses, children.
        """
        root = TreeService._get_root(db, individual_id)
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

        parents = db.query(Individual).filter(Individual.id.in_(parent_ids)).all() if parent_ids else []
        spouses = db.query(Individual).filter(Individual.id.in_(spouse_ids)).all() if spouse_ids else []
        children = db.query(Individual).filter(Individual.id.in_(child_ids)).all() if child_ids else []
        siblings = db.query(Individual).filter(Individual.id.in_(sibling_ids)).all() if sibling_ids else []

        # ------------------- RETURN SCHEMA ----------------------------------- #

        return ImmediateFamily(
            root=TreeService.to_schema(root),
            parents=[TreeService.to_schema(p) for p in parents],
            siblings=[TreeService.to_schema(s) for s in siblings],
            spouses=[TreeService.to_schema(s) for s in spouses],
            children=[TreeService.to_schema(c) for c in children],
        )