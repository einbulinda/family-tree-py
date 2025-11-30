from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession

from app.db.database import get_db
from app.graph.deps import get_neo4j_session
from app.services.graph_sync_service import GraphSyncService

router = APIRouter(prefix="/api/graph-admin", tags=["Graph Admin"])

@router.post("/sync")
def sync_graph(
        db:Session = Depends(get_db),
        neo4j: Neo4jSession = Depends(get_neo4j_session),
):
    try:
        result = GraphSyncService.sync_all(db,neo4j)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
