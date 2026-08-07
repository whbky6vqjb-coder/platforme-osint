from typing import Any, Dict, List
import json


class NodalGraphGenerator:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def generate(self, entities: List = None, pivots: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.nodes = []
        self.edges = []

        if entities:
            for entity in entities:
                self._add_node(entity)

        if pivots:
            for pivot in pivots:
                self._add_edge(pivot)

        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "format": "nodal",
            "renderer": "cytoscape",
        }

    def _add_node(self, entity):
        value = entity.value if hasattr(entity, "value") else str(entity)
        entity_type = entity.type if hasattr(entity, "type") else "unknown"
        confidence = entity.confidence if hasattr(entity, "confidence") else 0.5

        self.nodes.append({
            "id": value.lower()[:60],
            "label": f"{entity_type}: {value[:40]}",
            "type": entity_type,
            "confidence": confidence,
            "size": max(10, int(confidence * 50)),
            "color": self._node_color(entity_type, confidence),
        })

    def _add_edge(self, pivot):
        source = pivot.get("source", "")[:60]
        target = pivot.get("target", "")[:60]
        relation = pivot.get("relation", "connects")
        confidence = pivot.get("confidence", 0.5)

        if source and target:
            self.edges.append({
                "source": source,
                "target": target,
                "label": relation,
                "confidence": confidence,
                "width": max(1, int(confidence * 5)),
                "color": self._edge_color(confidence),
            })

    def _node_color(self, entity_type: str, confidence: float) -> str:
        base_colors = {
            "email": "#00d4aa",
            "ip": "#ff6b6b",
            "domain": "#4ecdc4",
            "company": "#a8e6cf",
            "person": "#dda0dd",
            "btc_address": "#f7931a",
            "eth_address": "#627eea",
            "sanction": "#ff4444",
        }
        base = base_colors.get(entity_type, "#00d4aa")
        if confidence < 0.3:
            return "#ff4444"
        elif confidence < 0.6:
            return "#ffaa00"
        return base

    def _edge_color(self, confidence: float) -> str:
        if confidence >= 0.7:
            return "#00ff88"
        elif confidence >= 0.4:
            return "#ffaa00"
        return "#ff4444"

    def to_cytoscape_json(self) -> str:
        return json.dumps({"elements": {"nodes": self.nodes, "edges": self.edges}}, indent=2)