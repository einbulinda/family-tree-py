from sqlalchemy.orm import Session
from app.models.individual import Individual
from app.schemas.individual_schema import IndividualCreate, IndividualUpdate

def create_individual(db:Session, individual_data:IndividualCreate):
    new_individual = Individual(**individual_data.model_dump())
    db.add(new_individual)
    db.commit()
    db.refresh(new_individual)
    return new_individual

def get_individual(db: Session, individual_id:int):
    return db.query(Individual).filter(Individual.id == individual_id).first()

def get_all_individuals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Individual).offset(skip).limit(limit).all()


def update_individual(db:Session, individual_id:int, updates:IndividualUpdate):
    individual = get_individual(db, individual_id)
    if not individual:
        return None

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(individual, key, value)

    db.commit()
    db.refresh(individual)
    return individual

def delete_individual(db:Session, individual_id:int):
    individual = get_individual(db, individual_id)
    if not individual:
        return None

    db.delete(individual)
    db.commit()
    return True