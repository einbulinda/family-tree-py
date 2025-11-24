from pydantic import BaseModel
from typing import List, Optional
from app.schemas.individual_schema import IndividualResponse

class ImmediateFamily(BaseModel):
    """
    Smart tree view focused on immediate family around a root individual.
    generation 0 = root
    generation -1 = parents
    generation +1 = children
    siblings & spouses are same generation as root.
    """
    root: IndividualResponse
    parents: List[IndividualResponse]
    siblings: List[IndividualResponse]
    spouses: List[IndividualResponse]
    children: List[IndividualResponse]

    class Config:
        from_attributes = True