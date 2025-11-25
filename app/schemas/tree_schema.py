from __future__ import annotations

from pydantic import BaseModel
from typing import List, Literal
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


class TreeNode(BaseModel):
    id: int
    label: str
    type: Literal["root", "parent", "spouse", "child", "sibling"]
    generation: int
    x: int
    y: int


class TreeEdge(BaseModel):
    source: int
    target: int
    relationship: str


class TreeVisualization(BaseModel):
    root: int
    nodes: List[TreeNode]
    edges: List[TreeEdge]
