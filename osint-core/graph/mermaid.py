from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class MermaidNode:
    id: str
    label: str
    shape: str = "box"
    color: str = "#00d4aa"


@dataclass
class MermaidEdge:
    source: str
    target: str
    label: str
    color: str = "#8899aa"


class MermaidGenerator:
    def __init__(self):
        self.nodes: List[MermaidNode] = []
        self.edges: List[MermaidEdge] = []
        self._node_ids: Dict[str, str] = {}

    def generate(self, entities: List = None, pivots: List[Dict[str, Any]] = None) -> str:
        self.nodes = []
        self.edges = []
        self._node_ids = {}

        if entities:
            for entity in entities:
                self._add_node(entity)

        if pivots:
            for pivot in pivots:
                self._add_edge(pivot)

        return self._render()

    def _add_node(self, entity):
        value = entity.value if hasattr(entity, "value") else str(entity)
        entity_type = entity.type if hasattr(entity, "type") else "unknown"

        node_id = self._get_node_id(value)
        if node_id in self._node_ids.values():
            return

        shape = self._get_shape(entity_type)
        color = self._get_color(entity_type)

        self.nodes.append(MermaidNode(
            id=node_id,
            label=f"{entity_type}: {value[:40]}",
            shape=shape,
            color=color,
        ))

    def _add_edge(self, pivot):
        source = pivot.get("source", "")
        target = pivot.get("target", "")
        relation = pivot.get("relation", "connects")
        confidence = pivot.get("confidence", 0.5)

        source_id = self._get_node_id(source)
        target_id = self._get_node_id(target)

        if source_id and target_id:
            edge_color = self._get_edge_color(confidence)
            self.edges.append(MermaidEdge(
                source=source_id,
                target=target_id,
                label=f"{relation} ({confidence:.2f})",
                color=edge_color,
            ))

    def _get_node_id(self, value: str) -> str:
        if value in self._node_ids:
            return self._node_ids[value]

        node_id = "node_" + value.lower().replace(" ", "_").replace(".", "_")[:40]
        node_id = "".join(c if c.isalnum() or c == "_" else "_" for c in node_id)
        self._node_ids[value] = node_id
        return node_id

    def _get_shape(self, entity_type: str) -> str:
        shapes = {
            "email": "email",
            "ip": "circle",
            "domain": "domain",
            "phone": "phone",
            "company": "stadium",
            "person": "person",
            "btc_address": "cylinder",
            "eth_address": "cylinder",
            "url": "link",
            "property": "house",
            "sanction": "alert",
        }
        return shapes.get(entity_type, "box")

    def _get_color(self, entity_type: str) -> str:
        colors = {
            "email": "#00d4aa",
            "ip": "#ff6b6b",
            "domain": "#4ecdc4",
            "phone": "#ffe66d",
            "company": "#a8e6cf",
            "person": "#dda0dd",
            "btc_address": "#f7931a",
            "eth_address": "#627eea",
            "url": "#87ceeb",
            "property": "#98d8c8",
            "sanction": "#ff4444",
        }
        return colors.get(entity_type, "#00d4aa")

    def _get_edge_color(self, confidence: float) -> str:
        if confidence >= 0.7:
            return "#00ff88"
        elif confidence >= 0.4:
            return "#ffaa00"
        else:
            return "#ff4444"

    def _render(self) -> str:
        lines = ["graph TD"]

        for node in self.nodes:
            label = node.label.replace('"', "'")
            lines.append(f'    {node.id}["{label}"]')

        for edge in self.edges:
            label = edge.label.replace('"', "'")
            lines.append(f'    {edge.source} -->|"{label}"| {edge.target}')

        return "\n".join(lines)