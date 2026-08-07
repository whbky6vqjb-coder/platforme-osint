import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class InvestigationResult:
    goal: str
    plan: Dict[str, Any]
    raw_results: Dict[str, Any]
    correlated_entities: List[Dict[str, Any]]
    pivots: List[Dict[str, Any]]
    trust_matrix: Dict[str, Any]
    graph_data: Dict[str, Any]
    mermaid_diagram: str
    report: str
    confidence: float
    timestamp: str


class InvestigationEngine:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.orchestrator = None
        self.reasoning_engine = None
        self.correlator = None
        self.trust_matrix = None
        self.graph_generator = None
        self.reporter = None

    async def run(self, goal: str) -> InvestigationResult:
        from osint_core.engine.orchestrator import OpenClawOrchestratorBridge
        from osint_core.engine.reasoning import HermesReasoningEngine
        from osint_core.correlator.pivoting import EntityCorrelator
        from osint_core.trust_matrix.triangulation import TrustMatrixBuilder
        from osint_core.graph.mermaid import MermaidGenerator
        from osint_core.graph.nodal import NodalGraphGenerator
        from osint_core.reporter import ReportGenerator

        self.orchestrator = OpenClawOrchestratorBridge(self.config.get("openclaw", {}))
        self.reasoning_engine = HermesReasoningEngine(self.config.get("hermes", {}).get("llm", {}))
        self.correlator = EntityCorrelator(self.config.get("correlation", {}))
        self.trust_matrix = TrustMatrixBuilder(self.config.get("trust_matrix", {}))
        self.graph_generator = MermaidGenerator()
        self.nodal_generator = NodalGraphGenerator()
        self.reporter = ReportGenerator()

        plan = await self.orchestrator.plan_investigation(goal, [])

        raw_results = await self.orchestrator.execute_plan(plan)

        entities = self.correlator.extract_entities(raw_results)
        pivots = self.correlator.perform_pivoting(entities)

        trust = self.trust_matrix.build(entities, pivots)

        mermaid = self.graph_generator.generate(entities, pivots)
        nodal = self.nodal_generator.generate(entities, pivots)

        reasoning_context = {
            "raw_results": raw_results,
            "entities": entities,
            "pivots": pivots,
            "trust": trust,
        }
        reasoning = await self.reasoning_engine.reason(goal, reasoning_context)

        report = self.reporter.generate(
            goal=goal,
            reasoning=reasoning,
            entities=entities,
            pivots=pivots,
            trust=trust,
            mermaid=mermaid,
            nodal=nodal,
            raw_results=raw_results,
        )

        return InvestigationResult(
            goal=goal,
            plan={"total_tasks": len(plan.tasks), "parallel_groups": plan.parallel_groups},
            raw_results=raw_results,
            correlated_entities=entities,
            pivots=pivots,
            trust_matrix=trust,
            graph_data={"mermaid": mermaid, "nodal": nodal},
            mermaid_diagram=mermaid,
            report=report,
            confidence=reasoning.confidence,
            timestamp=datetime.utcnow().isoformat(),
        )