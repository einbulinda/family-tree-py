from typing import Any, Dict, List
from neo4j import Session as Neo4jSession


class GraphTreeService:
    @staticmethod
    def get_ancestors(neo4j: Neo4jSession, person_id: int, max_depth: int = 4) -> List[Dict[str, Any]]:
        """
        Returns ancestors up to `max_depth` generations above.
        Each result includes the person's properties and the distance (generation).
        Uses the shortest path (minimum depth) in case of multiple paths.
        """
        if max_depth < 1:
            return []

        # Avoid injection: max_depth is used in a string, but it's an int from a trusted source
        # Still, ensure it's safe
        assert isinstance(max_depth, int) and max_depth > 0 and max_depth <= 100, "Invalid max_depth"

        query = f"""
            MATCH (root:Person {{id: $id}})
            MATCH path = (root)<-[:PARENT_OF*1..{max_depth}]-(ancestor:Person)
            WITH ancestor, min(length(path)) AS depth
            RETURN ancestor, depth
            ORDER BY depth ASC
        """

        result = neo4j.run(query, {"id": person_id})
        return [
            {
                "id": record["ancestor"]["id"],
                "name": record["ancestor"]["name"],
                "gender": record["ancestor"].get("gender"),
                "depth": record["depth"],
            }
            for record in result
        ]

    @staticmethod
    def get_descendants(neo4j: Neo4jSession, person_id: int, max_depth: int = 4) -> List[Dict[str, Any]]:
        """
        Returns descendants up to `max_depth` generations below.
        """
        query = """
        MATCH (root:Person {id: $id})
        MATCH path = (root)-[:PARENT_OF*1..$max_depth]->(desc:Person)
        WITH desc, length(path) as depth
        RETURN DISTINCT desc{.*, depth} AS node
        ORDER BY depth ASC
        """
        result = neo4j.run(query, {"id": person_id, "max_depth": max_depth})
        return [record["node"] for record in result]

    @staticmethod
    def get_full_tree(neo4j: Neo4jSession, person_id: int, max_depth: int = 4) -> Dict[str, Any]:
        """
        Simple combined view: root, ancestors, descendants.
        This is a JSON structure suitable for visualization in the next phase.
        """
        root_query = "MATCH (p:Person {id: $id}) RETURN p{.*} as node"
        root_res = neo4j.run(root_query, {"id": person_id}).single()
        if not root_res:
            return {}

        root = root_res["node"]

        ancestors = GraphTreeService.get_ancestors(neo4j, person_id, max_depth)
        descendants = GraphTreeService.get_descendants(neo4j, person_id, max_depth)

        return {
            "root": root,
            "ancestors": ancestors,
            "descendants": descendants,
        }
