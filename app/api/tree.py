from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.tree_schema import ImmediateFamily
from app.services.tree_service import TreeService

router = APIRouter(prefix="/api/tree", tags=["Tree"])

@router.get("/{individual_id}/immediate", response_model=ImmediateFamily)
def get_immediate_tree(individual_id: int, db: Session = Depends(get_db)):
    """
    Smart, human-friendly immediate family view for the given individual.
    """
    tree = TreeService.build_immediate_family(db, individual_id)
    if tree is None:
        raise HTTPException(status_code=404, detail="Individual not found")
    return tree