from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.tree_schema import ImmediateFamily, MultiLevelTree
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

@router.get("/{individual_id}/multi", response_model=MultiLevelTree)
def get_multi_level_tree(
    individual_id: int,
    direction: str = Query(
        "both", pattern="^(ancestors|descendants|both)$",
        description="Tree direction: ancestors, descendants, or both",
    ),
    max_depth: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
):
    tree = TreeService.build_multi_level_tree(
        db=db,
        individual_id=individual_id,
        direction=direction,
        max_depth=max_depth,
    )
    if not tree:
        raise HTTPException(status_code=404, detail="Individual not found")
    return tree