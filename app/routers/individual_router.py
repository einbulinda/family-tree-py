from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import individual_repository as repo
from app.schemas.individual_schema import IndividualCreate, IndividualUpdate, IndividualOut

router = APIRouter(prefix="/api/individuals", tags=["Individuals"])

@router.get("/", response_model=list[IndividualOut])
def list_individuals(db:Session = Depends(get_db)):
    return repo.get_all(db)

@router.get("/{individual_id}", response_model=IndividualOut)
def get_individual(individual_id: int, db: Session=Depends(get_db)):
    individual = repo.get_by_id(db,individual_id)
    if not individual:
        raise HTTPException(status_code=404, detail="Individual not found")
    return individual

@router.post("/", response_model=IndividualOut, status_code=201)
def create_individual(payload:IndividualCreate, db:Session = Depends(get_db)):
    return  repo.create(db, payload)

@router.put("/{individual_id}", response_model=IndividualOut)
def update_individual(individual_id: int, payload: IndividualUpdate, db:Session = Depends(get_db)):
    individual = repo.update(db, individual_id, payload)
    if not individual:
        raise HTTPException(status_code=404, detail="Individual not found")
    return  individual

@router.delete("/{individual_id}", status_code=204)
def delete_individual(individual_id:int, db:Session = Depends(get_db)):
    deleted = repo.delete(db, individual_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Individual not found")
    return None