from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.relationship import Relationship


def create_relationship(db: Session, data: dict):
    rel = Relationship(**data)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel

def individual_relationship(db: Session, individual_id: int):
    query = select(Relationship).where(Relationship.individual_id == individual_id)
    result = db.execute(query)
    return result.scalars().all()
