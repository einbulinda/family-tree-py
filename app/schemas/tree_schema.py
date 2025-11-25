from __future__ import annotations

from pydantic import BaseModel
from typing import List
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
    parents: List[IndividualResponse] =[]
    siblings: List[IndividualResponse] = []
    spouses: List[IndividualResponse] = []
    children: List[IndividualResponse] = []

class GenerationBand(BaseModel):
    """
    A single generation relative to the root.
    generation = 0  => root
    generation = -1 => parents
    generation = -2 => grandparents
    generation = +1 => children
    generation = +2 => grandchildren
    """
    generation : int
    individuals: List[IndividualResponse]

class MultiLevelTree(BaseModel):
    """
    Multi-level tree suitable for visualizations (FamilySearch-style).
    """
    root: IndividualResponse
    generations: List[GenerationBand]
