from sqlalchemy.orm import Session
from app.services.tree_service import TreeService
from app.schemas.tree_schema import TreeVisualization, TreeNode, TreeEdge


class TreeVisualService:

    @staticmethod
    def build_tree_visual(db: Session, individual_id: int) -> TreeVisualization | None:
        fam = TreeService.build_immediate_family(db, individual_id)

        if fam is None:
            return None

        root = fam.root

        nodes = []
        edges = []

        # Helper to place nodes
        def add_node(ind, type, gen, x, y):
            nodes.append(TreeNode(
                id=ind.id,
                label=f"{ind.first_name} {ind.last_name}".strip(),
                type=type,
                generation=gen,
                x=x,
                y=y,
            ))

        # Root at center
        add_node(root, "root", 0, x=0, y=0)

        # Spouse on right
        for i, sp in enumerate(fam.spouses):
            add_node(sp, "spouse", 0, x=150, y=0)
            edges.append(TreeEdge(
                source=root.id, target=sp.id, relationship="spouse"
            ))

        # Parents above root
        for i, p in enumerate(fam.parents):
            add_node(p, "parent", -1, x=-150 + (i * 150), y=-120)
            edges.append(TreeEdge(
                source=p.id, target=root.id, relationship="parent"
            ))

        # Children below
        for i, c in enumerate(fam.children):
            add_node(c, "child", 1, x=-75 + (i * 150), y=120)

            # parent edge
            edges.append(TreeEdge(
                source=root.id, target=c.id, relationship="parent"
            ))

            # spouse parent link
            for sp in fam.spouses:
                edges.append(TreeEdge(
                    source=sp.id, target=c.id, relationship="parent"
                ))

        # Siblings
        for i, s in enumerate(fam.siblings):
            add_node(s, "sibling", 0, x=-150 - (i * 150), y=0)
            edges.append(TreeEdge(
                source=s.id, target=root.id, relationship="sibling"
            ))

        return TreeVisualization(
            root=root.id,
            nodes=nodes,
            edges=edges
        )
