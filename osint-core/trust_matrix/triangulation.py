from typing import Any, Dict, List
from dataclasses import dataclass, field


@dataclass
class Evidence:
    source: str
    category: str
    content: str
    reliability: float
    timestamp: str = ""


@dataclass
class TrustScore:
    entity: str
    legal_score: float = 0.0
    technical_score: float = 0.0
    physical_score: float = 0.0
    combined_score: float = 0.0
    evidence_count: int = 0
    confidence: float = 0.0


class TrustMatrixBuilder:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.legal_weight = self.config.get("legal_weight", 0.4)
        self.technical_weight = self.config.get("technical_weight", 0.35)
        self.physical_weight = self.config.get("physical_weight", 0.25)

    def build(self, entities: List, pivots: List[Dict[str, Any]]) -> Dict[str, Any]:
        trust_scores = {}
        evidence_map = {}

        for entity in entities:
            score = self._score_entity(entity, pivots)
            trust_scores[entity.value] = score
            evidence_map[entity.value] = self._collect_evidence(entity, pivots)

        return {
            "scores": trust_scores,
            "evidence": evidence_map,
            "weights": {
                "legal": self.legal_weight,
                "technical": self.technical_weight,
                "physical": self.physical_weight,
            },
            "method": "Faisceau de preuves triangule",
            "total_entities": len(entities),
            "total_pivots": len(pivots),
        }

    def _score_entity(self, entity, pivots):
        legal = self._legal_score(entity, pivots)
        technical = self._technical_score(entity, pivots)
        physical = self._physical_score(entity, pivots)

        combined = (
            legal * self.legal_weight
            + technical * self.technical_weight
            + physical * self.physical_weight
        )

        return TrustScore(
            entity=entity.value,
            legal_score=legal,
            technical_score=technical,
            physical_score=physical,
            combined_score=combined,
            evidence_count=len(pivots),
            confidence=combined,
        )

    def _legal_score(self, entity, pivots) -> float:
        score = 0.3
        for pivot in pivots:
            if pivot.get("relation") in ("registered_at", "legal_entity", "company_registry"):
                score += 0.2
            if pivot.get("relation") in ("sanction_match", "pep_match"):
                score -= 0.3
        return min(max(score, 0.0), 1.0)

    def _technical_score(self, entity, pivots) -> float:
        score = 0.3
        for pivot in pivots:
            if pivot.get("relation") in ("ip_address", "domain", "ssl_cert", "dns_record"):
                score += 0.15
            if pivot.get("relation") in ("email", "phone"):
                score += 0.1
        return min(max(score, 0.0), 1.0)

    def _physical_score(self, entity, pivots) -> float:
        score = 0.2
        for pivot in pivots:
            if pivot.get("relation") in ("property_record", "cadastre", "foncier"):
                score += 0.25
            if pivot.get("relation") in ("satellite_imagery", "energy_connection"):
                score += 0.2
        return min(max(score, 0.0), 1.0)

    def _collect_evidence(self, entity, pivots) -> List[Dict[str, Any]]:
        evidence = []
        for pivot in pivots:
            if entity.value in (pivot.get("source", ""), pivot.get("target", "")):
                evidence.append({
                    "source": pivot.get("source", ""),
                    "target": pivot.get("target", ""),
                    "relation": pivot.get("relation", ""),
                    "confidence": pivot.get("confidence", 0.0),
                })
        return evidence