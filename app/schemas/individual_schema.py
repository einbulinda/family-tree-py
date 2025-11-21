from pydantic import BaseModel
from typing import Optional
from datetime import date

class IndividualBase(BaseModel):
    first_name:str
    last_name: str
    gender: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    is_alive: Optional[bool] = True
    bio: Optional[str] = None
    photo_url: Optional[str] = None

class IndividualCreate(IndividualBase):
    pass

class IndividualUpdate(IndividualBase):
    pass

class IndividualResponse(IndividualBase):
    id:int

    class Config:
        orm_mode = True
