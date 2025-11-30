from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Session as Neo4jSession

from app.graph.deps import get_neo4j_session
from app.services.graph_tree_service import GraphTreeService

router = APIRouter(prefix="/api/graph-tree", tags=["Graph Tree"])

@router.get("/{person_id}/ancestors")
def get_ancestors(
    person_id: int,
    max_depth: int = Query(4, ge=1, le=10),
    neo4j: Neo4jSession = Depends(get_neo4j_session),
):
    data = GraphTreeService.get_ancestors(neo4j, person_id, max_depth)
    if not data:
        raise HTTPException(status_code=404, detail="Person not found or no ancestors")
    return {"person_id": person_id, "ancestors": data}


@router.get("/{person_id}/descendants")
def get_descendants(
    person_id: int,
    max_depth: int = Query(4, ge=1, le=10),
    neo4j: Neo4jSession = Depends(get_neo4j_session),
):
    data = GraphTreeService.get_descendants(neo4j, person_id, max_depth)
    return {"person_id": person_id, "descendants": data}


@router.get("/{person_id}/full")
def get_full_tree(
    person_id: int,
    max_depth: int = Query(4, ge=1, le=10),
    neo4j: Neo4jSession = Depends(get_neo4j_session),
):
    data = GraphTreeService.get_full_tree(neo4j, person_id, max_depth)
    if not data:
        raise HTTPException(status_code=404, detail="Person not found")
    return data