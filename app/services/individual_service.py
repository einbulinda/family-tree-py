from sqlalchemy.orm import Session
from app.repositories.individual_repository import (
create_individual, get_individual, get_all_individuals, update_individual, delete_individual
)

from app.schemas.individual_schema import IndividualCreate, IndividualUpdate

class IndividualService:

    @staticmethod
    def create(db:Session, data: IndividualCreate):
        return create_individual(db, data)

    @staticmethod
    def get(db:Session, individual_id:int):
        return get_individual(db, individual_id)

    @staticmethod
    def list(db:Session, skip:int, limit:int):
        return get_all_individuals(db,skip,limit)

    @staticmethod
    def update(db:Session, individual_id:int, data:IndividualUpdate):
        return update_individual(db, individual_id,data)

    @staticmethod
    def delete(db:Session, individual_id:int):
        return delete_individual(db, individual_id)