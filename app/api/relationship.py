from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.relationship_service import RelationshipService
from app.schemas.relationship_schema import RelationshipCreate, RelationshipResponse

router = APIRouter(prefix="/api/relationships", tags=["Relationships"])

@router.post("/", response_model=RelationshipResponse)
def add_relationship(payload: RelationshipCreate, db: Session = Depends(get_db)):
    try:
        rel = RelationshipService.add_relationship(
            db,
            payload.individual_id,
            payload.related_individual_id,
            payload.relationship_type,
        )
        return rel
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{individual_id}", response_model=list[RelationshipResponse])
def get_relationships(individual_id: int, db: Session = Depends(get_db)):
    return RelationshipService.get_relationships(db, individual_id)