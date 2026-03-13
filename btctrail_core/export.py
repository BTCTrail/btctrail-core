import json
import networkx as nx
from typing import Dict, Any

class GraphExporter:
    """
    Exports networkx graphs to various structured formats.
    """

    @staticmethod
    def to_d3_json(graph: nx.DiGraph) -> str:
        """
        Converts a networkx graph into a JSON format compatible with D3 forced-directed layouts.
        Format: {"nodes": [...], "links": [...]}
        """
        nodes = []
        for node, attrs in graph.nodes(data=True):
            nodes.append({
                "id": node,
                "type": attrs.get("type", "unknown"),
                "label": attrs.get("label", node),
                "is_change": attrs.get("is_change", False),
                "privacy_leak": attrs.get("privacy_leak", False)
            })

        links = []
        for source, target, attrs in graph.edges(data=True):
            links.append({
                "source": source,
                "target": target,
                "value": attrs.get("value", 0),
                "is_change": attrs.get("is_change", False),
                "type": attrs.get("type", "flow")
            })

        return json.dumps({"nodes": nodes, "links": links}, indent=2)

    @staticmethod
    def save_to_file(data: str, filename: str):
        with open(filename, 'w') as f:
            f.write(data)
