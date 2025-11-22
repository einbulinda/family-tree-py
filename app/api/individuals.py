from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.individual_schema import IndividualCreate, IndividualUpdate, IndividualResponse
from app.services.individual_service import IndividualService

router = APIRouter(prefix="/api/individuals", tags=["Individuals"])

@router.get("/", response_model=list[IndividualResponse])
def list_individuals(skip:int = 0, limit:int = 100,db:Session = Depends(get_db)):
    return IndividualService.list(db,skip, limit)

@router.get("/{individual_id}", response_model=IndividualResponse)
def get_individual(individual_id: int, db: Session=Depends(get_db)):
    individual = IndividualService.get(db,individual_id)
    if not individual:
        raise HTTPException(status_code=404, detail="Individual not found")
    return individual

@router.post("/", response_model=IndividualResponse, status_code=201)
def create_individual(payload:IndividualCreate, db:Session = Depends(get_db)):
    return  IndividualService.create(db, payload)

@router.put("/{individual_id}", response_model=IndividualResponse)
def update_individual(individual_id: int, payload: IndividualUpdate, db:Session = Depends(get_db)):
    updated = IndividualService.update(db, individual_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Individual not found")
    return  updated

@router.delete("/{individual_id}", status_code=200)
def delete_individual(individual_id:int, db:Session = Depends(get_db)):
    deleted = IndividualService.delete(db, individual_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Individual not found")
    return {"message":"Individual deleted"}
