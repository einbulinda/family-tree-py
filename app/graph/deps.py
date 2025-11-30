from typing import Generator
from neo4j import Session
from fastapi import Depends

from app.graph.neo4j_client import neo4j_session


def get_neo4j_session() -> Generator[Session, None, None]:
    with neo4j_session() as session:
        yield session
