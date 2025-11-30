from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession

from app.models.individual import Individual
from app.models.relationship import Relationship

class GraphSyncService:
    @staticmethod
    def sync_all(db:Session, neo4j: Neo4jSession) -> dict:
        """
        Simple full-sync: wipes existing Person graph and rebuilds from Postgres.
        Call this from an admin endpoint.
        """
        # 1) Clear existing graph data (only Person / relationships)
        neo4j.run(
            """        
            MATCH (p:Person)-[r]->()
            DELETE r
            """
        )
        neo4j.run(
            """
            MATCH (p:Person)
            DELETE p
            """
        )

        # 2) Sync Persons
        individuals = db.query(Individual).all()
        for ind in individuals:
            neo4j.run(
                """
                CREATE (p:Person {
                    id: $id,
                    first_name: $first_name,
                    last_name: $last_name,
                    gender: $gender,
                    birth_date: $birth_date,
                    death_date: $death_date
                })
                """,
                {
                    "id": ind.id,
                    "first_name": ind.first_name,
                    "last_name": ind.last_name,
                    "gender": ind.gender,
                    "birth_date": ind.birth_date.isoformat() if ind.birth_date else None,
                    "death_date": ind.death_date.isoformat() if ind.death_date else None,
                },
            )

        # 3) Sync relationships
        rels = db.query(Relationship).all()
        for rel in rels:
            if rel.relationship_type == "spouse":
                # create an undirected-like pair of links so traversal is easier
                neo4j.run(
                    """
                    MATCH (a:Person {id: $a_id}), (b:Person {id: $b_id})
                    MERGE (a)-[:SPOUSE_OF]->(b)
                    MERGE (b)-[:SPOUSE_OF]->(a)
                    """,
                    {"a_id": rel.individual_id, "b_id": rel.related_individual_id},
                )
            elif rel.relationship_type in ("parent", "child"):
                # We normalise to PARENT_OF direction
                if rel.relationship_type == "parent":
                    parent_id = rel.individual_id
                    child_id = rel.related_individual_id
                else:
                    parent_id = rel.related_individual_id
                    child_id = rel.individual_id

                neo4j.run(
                    """
                    MATCH (p:Person {id: $parent_id}), (c:Person {id: $child_id})
                    MERGE (p)-[:PARENT_OF]->(c)
                    """,
                    {"parent_id": parent_id, "child_id": child_id},
                )
        return {"individuals_synced": len(individuals), "relationships_synced": len(rels)}
