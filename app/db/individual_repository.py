from sqlalchemy.orm import Session
from app.models.individual_model import Individual
from app.schemas.individual_schema import IndividualCreate, IndividualUpdate

def get_all(db: Session):
    return db.query(Individual).all()

def get_by_id(db: Session, individual_id:int):
    return db.query(Individual).filter(Individual.id == individual_id).first()

def create(db:Session, payload:IndividualCreate):
    individual = Individual(**payload.model_dump())
    db.add(individual)
    db.commit()
    db.refresh(individual)
    return individual

def update(db:Session, individual_id:int, payload:IndividualUpdate):
    individual = get_by_id(db, individual_id)
    if not individual:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(individual, key, value)

    db.commit()
    db.refresh(individual)
    return individual

def delete(db:Session, individual_id:int):
    individual = get_by_id(db, individual_id)
    if not individual:
        return None

    db.delete(individual)
    db.commit()
    return True