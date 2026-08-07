from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Pivot:
    source_entity: str
    source_type: str
    relation: str
    target_entity: str
    target_type: str
    path: List[str]
    confidence: float = 0.0
    evidence_count: int = 0


@dataclass
class PivotChain:
    start_entity: str
    end_entity: str
    chain: List[Pivot]
    total_confidence: float
    path_description: str


class EntityCorrelator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_depth = self.config.get("max_depth", 4)
        self.trust_threshold = self.config.get("trust_threshold", 0.5)
        self.entities: List = []
        self.relations: Dict[str, List[Dict]] = defaultdict(list)
        self.pivots: List[Pivot] = []

    def add_entities(self, entities: List):
        self.entities.extend(entities)

    def build_relations(self):
        from osint_core.storage.manager import StorageManager

        storage = StorageManager()
        for entity in self.entities:
            storage.add_relation(
                source=entity.value,
                relation=entity.type,
                target=entity.source_tool,
                meta={"confidence": entity.confidence, "source_query": entity.source_query},
            )

    def find_connections(self, entity_a: str, entity_b: str, max_depth: int = 3) -> List[Pivot]:
        connections = []
        visited = set()

        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth or current in visited:
                return
            visited.add(current)

            for rel in self.relations.get(current, []):
                target = rel.get("target", "")
                if target == entity_b:
                    connections.append(Pivot(
                        source_entity=current,
                        source_type=rel.get("relation", ""),
                        relation=rel.get("relation", ""),
                        target_entity=target,
                        target_type="",
                        path=path + [target],
                        confidence=rel.get("metadata", {}).get("confidence", 0.5),
                        evidence_count=1,
                    ))
                elif target not in visited:
                    dfs(target, path + [target], depth + 1)

        dfs(entity_a, [entity_a], 0)
        return connections

    def perform_pivoting(self, entities: List) -> List[Dict[str, Any]]:
        pivots = []
        entity_values = [e.value for e in entities]

        for i, entity_a in enumerate(entity_values):
            for j, entity_b in enumerate(entity_values):
                if i >= j:
                    continue
                connections = self.find_connections(entity_a, entity_b, self.max_depth)
                if connections:
                    for conn in connections:
                        pivots.append({
                            "source": entity_a,
                            "target": entity_b,
                            "path": conn.path,
                            "confidence": conn.total_confidence if hasattr(conn, 'total_confidence') else conn.confidence,
                            "relation": conn.relation,
                        })

        return pivots

    def get_all_entities(self) -> List[Dict[str, Any]]:
        result = []
        for entity in self.entities:
            result.append({
                "name": entity.value,
                "type": entity.type,
                "source_tool": entity.source_tool,
                "confidence": entity.confidence,
                "metadata": entity.metadata,
            })
        return result

    def get_entity_summary(self) -> Dict[str, Any]:
        type_counts = defaultdict(int)
        for entity in self.entities:
            type_counts[entity.type] += 1

        return {
            "total_entities": len(self.entities),
            "by_type": dict(type_counts),
            "unique_values": len(set(e.value for e in self.entities)),
            "avg_confidence": sum(e.confidence for e in self.entities) / max(len(self.entities), 1),
        }