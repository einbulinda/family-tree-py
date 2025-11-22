from sqlalchemy.orm import Session
from app.repositories.relationship_repository import (create_relationship, individual_relationship)
from app.services.individual_service import IndividualService

VALID_TYPES = {"parent", "child", "spouse"}

class RelationshipService:

    @staticmethod
    def add_relationship(db: Session, individual_id: int, related_id: int, rel_type: str):
        if rel_type not in VALID_TYPES:
            raise ValueError("Invalid relationship type")

        # Ensure both individuals exist
        ind1 = IndividualService.get(db, individual_id)
        ind2 = IndividualService.get(db, related_id)
        if not ind1 or not ind2:
            raise ValueError("Individual does not exist")

        # Additional rule: a person cannot be their own relative
        if individual_id == related_id:
            raise ValueError("Cannot relate an individual to themselves")

        data = {
            "individual_id": individual_id,
            "related_individual_id": related_id,
            "relationship_type": rel_type,
        }

        return  create_relationship(db, data)

    @staticmethod
    async def get_relationships(db: Session, individual_id: int):
        return individual_relationship(db, individual_id)
