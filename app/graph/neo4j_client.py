from contextlib import contextmanager
from typing import Generator, Optional

from neo4j import GraphDatabase, Driver
from app.core.config import settings

_driver: Optional[Driver] = None

def get_driver() -> Driver:
    global _driver
    if _driver is None:
        if not (settings.NEO4J_URI and settings.NEO4J_USER and settings.NEO4J_PASSWORD):
            raise RuntimeError("Neo4j is not configured. Check NEO4J_* env vars.")
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    return _driver

@contextmanager
def neo4j_session():
    """
    Simple context manager for a Neo4j session.
    Usage:
        with neo4j_session() as session:
            result = session.run("MATCH (n) RETURN n LIMIT 1")
    """
    driver = get_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()