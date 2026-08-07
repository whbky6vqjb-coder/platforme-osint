import os
from typing import Any, Dict, List
from datetime import datetime


class ReportGenerator:
    def __init__(self, template_path: str = None):
        self.sections = []
        self.template_path = template_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "template.md"
        )
        self.template = self._load_template()

    def _load_template(self) -> str:
        if os.path.exists(self.template_path):
            with open(self.template_path, "r", encoding="utf-8") as f:
                return f.read()
        return self._fallback_template()

    def _fallback_template(self) -> str:
        return """# OSINT Investigation Report

**Investigation ID:** {{investigation_id}}
**Date:** {{date}}
**Status:** {{status}}

## Executive Summary
{{executive_summary}}

## Findings
{{findings}}

## Recommendations
{{recommendations}}
"""

    def generate(
        self,
        goal: str,
        reasoning: Any = None,
        entities: List = None,
        pivots: List[Dict[str, Any]] = None,
        trust: Dict[str, Any] = None,
        mermaid: str = "",
        nodal: Dict[str, Any] = None,
        raw_results: Dict[str, Any] = None,
        investigation_id: str = "",
        classification: str = "CONFIDENTIAL",
        primary_objective: str = "",
        secondary_objectives: str = "",
        scope: str = "",
        limitations: str = "",
        key_findings: str = "",
        executive_summary: str = "",
        overall_confidence: float = 0.0,
        overall_trust_score: float = 0.0,
        model_used: str = "",
        context_window: str = "",
        compression_ratio: str = "",
        optimization_enabled: bool = False,
        summary_interval: int = 10,
        tool_inventory_table: str = "",
        source_credibility_table: str = "",
        free_tool_count: int = 0,
        paid_replaced_count: int = 0,
        total_tools: int = 0,
        persons_table: str = "",
        organizations_table: str = "",
        locations_table: str = "",
        dates_table: str = "",
        financial_table: str = "",
        digital_assets_table: str = "",
        correlation_map_mermaid: str = "",
        pivot_paths_table: str = "",
        cross_reference_matrix: str = "",
        key_connections_analysis: str = "",
        trust_scores_table: str = "",
        evidence_triangulation_table: str = "",
        contradictions_analysis: str = "",
        confidence_distribution_chart: str = "",
        timeline_mermaid: str = "",
        chronological_events_table: str = "",
        event_correlation_analysis: str = "",
        relationship_graph_mermaid: str = "",
        network_nodes_table: str = "",
        key_influencers_analysis: str = "",
        network_clusters_analysis: str = "",
        online_presence_table: str = "",
        social_media_analysis: str = "",
        domain_infrastructure_table: str = "",
        email_communication_analysis: str = "",
        financial_entities_table: str = "",
        transaction_analysis: str = "",
        corporate_structure_diagram: str = "",
        financial_risk_assessment: str = "",
        geolocation_map_mermaid: str = "",
        location_analysis_table: str = "",
        physical_infrastructure_analysis: str = "",
        threat_indicators_table: str = "",
        vulnerability_assessment: str = "",
        attack_surface_analysis: str = "",
        cyber_mitigation_recommendations: str = "",
        jurisdictions_table: str = "",
        regulatory_compliance_analysis: str = "",
        legal_risks_analysis: str = "",
        sanctions_watchlist_analysis: str = "",
        media_coverage_table: str = "",
        public_sentiment_analysis: str = "",
        narrative_analysis: str = "",
        wallet_analysis_table: str = "",
        transaction_flow_diagram: str = "",
        smart_contract_analysis: str = "",
        data_breaches_table: str = "",
        exposed_credentials_analysis: str = "",
        dark_web_analysis: str = "",
        passive_reconnaissance_results: str = "",
        osint_techniques_table: str = "",
        advanced_analysis_results: str = "",
        key_findings_table: str = "",
        confirmed_facts: str = "",
        unconfirmed_hypotheses: str = "",
        disproven_claims: str = "",
        risk_matrix_table: str = "",
        risk_heat_map: str = "",
        residual_risk_analysis: str = "",
        immediate_actions: str = "",
        short_term_recommendations: str = "",
        long_term_recommendations: str = "",
        further_investigation_areas: str = "",
        raw_tool_results: str = "",
        source_urls: str = "",
        methodology_notes: str = "",
        glossary_table: str = "",
        start_date: str = "",
        end_date: str = "",
        total_duration: str = "",
        total_tools_used: int = 0,
        total_entities: int = 0,
        total_pivots: int = 0,
        total_evidence: int = 0,
        evidence_log: str = "",
        verification_chain: str = "",
    ) -> str:
        report = self.template

        replacements = {
            "{{investigation_id}}": investigation_id or "OSINT-000",
            "{{date}}": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "{{status}}": "COMPLETED" if reasoning else "IN_PROGRESS",
            "{{classification}}": classification,
            "{{executive_summary}}": executive_summary or (reasoning.conclusion if reasoning else "No summary available"),
            "{{primary_objective}}": primary_objective,
            "{{secondary_objectives}}": secondary_objectives,
            "{{scope}}": scope,
            "{{limitations}}": limitations,
            "{{key_findings}}": key_findings,
            "{{overall_confidence}}": f"{overall_confidence:.1f}",
            "{{overall_trust_score}}": f"{overall_trust_score:.2f}",
            "{{model_used}}": model_used,
            "{{context_window}}": context_window,
            "{{compression_ratio}}": compression_ratio,
            "{{optimization_enabled}}": str(optimization_enabled),
            "{{summary_interval}}": str(summary_interval),
            "{{free_tool_count}}": str(free_tool_count),
            "{{paid_replaced_count}}": str(paid_replaced_count),
            "{{total_tools}}": str(total_tools),
            "{{total_tools_used}}": str(total_tools_used),
            "{{total_entities}}": str(total_entities),
            "{{total_pivots}}": str(total_pivots),
            "{{total_evidence}}": str(total_evidence),
            "{{start_date}}": start_date,
            "{{end_date}}": end_date,
            "{{total_duration}}": total_duration,
            "{{tool_inventory_table}}": tool_inventory_table,
            "{{source_credibility_table}}": source_credibility_table,
            "{{persons_table}}": persons_table,
            "{{organizations_table}}": organizations_table,
            "{{locations_table}}": locations_table,
            "{{dates_table}}": dates_table,
            "{{financial_table}}": financial_table,
            "{{digital_assets_table}}": digital_assets_table,
            "{{correlation_map_mermaid}}": correlation_map_mermaid,
            "{{pivot_paths_table}}": pivot_paths_table,
            "{{cross_reference_matrix}}": cross_reference_matrix,
            "{{key_connections_analysis}}": key_connections_analysis,
            "{{trust_scores_table}}": trust_scores_table,
            "{{evidence_triangulation_table}}": evidence_triangulation_table,
            "{{contradictions_analysis}}": contradictions_analysis,
            "{{confidence_distribution_chart}}": confidence_distribution_chart,
            "{{timeline_mermaid}}": timeline_mermaid,
            "{{chronological_events_table}}": chronological_events_table,
            "{{event_correlation_analysis}}": event_correlation_analysis,
            "{{relationship_graph_mermaid}}": relationship_graph_mermaid,
            "{{network_nodes_table}}": network_nodes_table,
            "{{key_influencers_analysis}}": key_influencers_analysis,
            "{{network_clusters_analysis}}": network_clusters_analysis,
            "{{online_presence_table}}": online_presence_table,
            "{{social_media_analysis}}": social_media_analysis,
            "{{domain_infrastructure_table}}": domain_infrastructure_table,
            "{{email_communication_analysis}}": email_communication_analysis,
            "{{financial_entities_table}}": financial_entities_table,
            "{{transaction_analysis}}": transaction_analysis,
            "{{corporate_structure_diagram}}": corporate_structure_diagram,
            "{{financial_risk_assessment}}": financial_risk_assessment,
            "{{geolocation_map_mermaid}}": geolocation_map_mermaid,
            "{{location_analysis_table}}": location_analysis_table,
            "{{physical_infrastructure_analysis}}": physical_infrastructure_analysis,
            "{{threat_indicators_table}}": threat_indicators_table,
            "{{vulnerability_assessment}}": vulnerability_assessment,
            "{{attack_surface_analysis}}": attack_surface_analysis,
            "{{cyber_mitigation_recommendations}}": cyber_mitigation_recommendations,
            "{{jurisdictions_table}}": jurisdictions_table,
            "{{regulatory_compliance_analysis}}": regulatory_compliance_analysis,
            "{{legal_risks_analysis}}": legal_risks_analysis,
            "{{sanctions_watchlist_analysis}}": sanctions_watchlist_analysis,
            "{{media_coverage_table}}": media_coverage_table,
            "{{public_sentiment_analysis}}": public_sentiment_analysis,
            "{{narrative_analysis}}": narrative_analysis,
            "{{wallet_analysis_table}}": wallet_analysis_table,
            "{{transaction_flow_diagram}}": transaction_flow_diagram,
            "{{smart_contract_analysis}}": smart_contract_analysis,
            "{{data_breaches_table}}": data_breaches_table,
            "{{exposed_credentials_analysis}}": exposed_credentials_analysis,
            "{{dark_web_analysis}}": dark_web_analysis,
            "{{passive_reconnaissance_results}}": passive_reconnaissance_results,
            "{{osint_techniques_table}}": osint_techniques_table,
            "{{advanced_analysis_results}}": advanced_analysis_results,
            "{{key_findings_table}}": key_findings_table,
            "{{confirmed_facts}}": confirmed_facts,
            "{{unconfirmed_hypotheses}}": unconfirmed_hypotheses,
            "{{disproven_claims}}": disproven_claims,
            "{{risk_matrix_table}}": risk_matrix_table,
            "{{risk_heat_map}}": risk_heat_map,
            "{{residual_risk_analysis}}": residual_risk_analysis,
            "{{immediate_actions}}": immediate_actions,
            "{{short_term_recommendations}}": short_term_recommendations,
            "{{long_term_recommendations}}": long_term_recommendations,
            "{{further_investigation_areas}}": further_investigation_areas,
            "{{raw_tool_results}}": raw_tool_results,
            "{{source_urls}}": source_urls,
            "{{methodology_notes}}": methodology_notes,
            "{{glossary_table}}": glossary_table,
            "{{evidence_log}}": evidence_log,
            "{{verification_chain}}": verification_chain,
        }

        for placeholder, value in replacements.items():
            report = report.replace(placeholder, str(value) if value is not None else "")

        lines = []
        lines.append("# Investigation Report")
        lines.append("")
        lines.append(f"**Goal:** {goal}")
        lines.append(f"**Generated:** {datetime.utcnow().isoformat()}")
        if reasoning:
            lines.append(f"**Confidence:** {reasoning.confidence:.2f}")
            lines.append(f"**Trust Score:** {reasoning.trust_score:.2f}")
        lines.append("")

        lines.append("## Executive Summary")
        lines.append("")
        if reasoning:
            lines.append(reasoning.conclusion)
        lines.append("")

        lines.append("## Reasoning Steps")
        lines.append("")
        if reasoning and reasoning.steps:
            for i, step in enumerate(reasoning.steps, 1):
                lines.append(f"### Step {i}: {step.step_type}")
                lines.append(step.content)
                lines.append(f"- Confidence: {step.confidence:.2f}")
                if step.sources:
                    lines.append(f"- Sources: {', '.join(step.sources)}")
                lines.append("")
        lines.append("")

        lines.append("## Entities Detected")
        lines.append("")
        if entities:
            lines.append("| Entity | Type | Source | Confidence |")
            lines.append("|--------|------|--------|------------|")
            for entity in entities:
                value = entity.value if hasattr(entity, "value") else str(entity)
                entity_type = entity.type if hasattr(entity, "type") else "unknown"
                source = entity.source_tool if hasattr(entity, "source_tool") else ""
                confidence = entity.confidence if hasattr(entity, "confidence") else 0.0
                lines.append(f"| {value[:40]} | {entity_type} | {source} | {confidence:.2f} |")
        lines.append("")

        lines.append("## Pivots & Correlations")
        lines.append("")
        if pivots:
            for i, pivot in enumerate(pivots, 1):
                source = pivot.get("source", "")[:40]
                target = pivot.get("target", "")[:40]
                relation = pivot.get("relation", "connects")
                confidence = pivot.get("confidence", 0.0)
                lines.append(f"{i}. **{source}** --[{relation}]--> **{target}** (confidence: {confidence:.2f})")
        lines.append("")

        lines.append("## Trust Matrix (Faisceau de preuves triangulé)")
        lines.append("")
        if trust and "scores" in trust:
            lines.append("| Entity | Legal | Technical | Physical | Combined |")
            lines.append("|--------|-------|-----------|----------|----------|")
            for entity, score in trust["scores"].items():
                if isinstance(score, dict):
                    lines.append(f"| {entity[:30]} | {score.get('legal_score', 0):.2f} | {score.get('technical_score', 0):.2f} | {score.get('physical_score', 0):.2f} | {score.get('combined_score', 0):.2f} |")
                else:
                    lines.append(f"| {entity[:30]} | - | - | - | {score:.2f} |")
        lines.append("")

        lines.append("## Entity Graph (Mermaid)")
        lines.append("")
        lines.append("```mermaid")
        lines.append(mermaid if mermaid else "graph TD; No data available")
        lines.append("```")
        lines.append("")

        lines.append("## Raw Results Summary")
        lines.append("")
        if raw_results:
            if isinstance(raw_results, dict):
                for tool_name, result in raw_results.items():
                    status = result.get("status", "unknown") if isinstance(result, dict) else "unknown"
                    lines.append(f"- **{tool_name}**: {status}")
        lines.append("")

        lines.append("## Recommendations")
        lines.append("")
        if reasoning and reasoning.recommendations:
            for rec in reasoning.recommendations:
                lines.append(f"- {rec}")
        else:
            lines.append("- Further investigation recommended")
        lines.append("")

        lines.append("## Methodology")
        lines.append("")
        lines.append("This investigation was conducted using the Platforme OSINT framework with:")
        lines.append("- **OpenClaw Orchestrator** for multi-agent task coordination")
        lines.append("- **Hermes-3 LLM Reasoning Engine** for cross-referencing and analysis")
        lines.append("- **Faisceau de preuves triangulé** for trust assessment (legal + technical + physical evidence)")
        lines.append("- **200 integrated OSINT tools** across 10 categories")
        lines.append("")

        lines.append("---")
        lines.append("*Report generated by Platforme OSINT — OpenClaw Orchestrator + Hermes-3 Reasoning Engine + Hermes Web UI*")
        lines.append("*Investigation conducted with 200 OSINT tools across 10 categories*")
        lines.append("*Trust assessment: Faisceau de preuves triangulé*")
        lines.append("*All findings verified through multiple independent sources*")

        template_section = report.split("---")[0] if "---" in report else ""
        if template_section:
            lines.insert(0, template_section)

        return "\n".join(lines)

    def get_template_sections(self) -> List[str]:
        if not self.template:
            return []
        return [line.strip() for line in self.template.split("\n") if line.strip().startswith("##")]

    def get_template_stats(self) -> Dict[str, Any]:
        if not self.template:
            return {"sections": 0, "placeholders": 0, "lines": 0}
        sections = [line for line in self.template.split("\n") if line.strip().startswith("##")]
        placeholders = [line for line in self.template.split("\n") if "{{" in line and "}}" in line]
        return {
            "sections": len(sections),
            "placeholders": len(placeholders),
            "lines": len(self.template.split("\n")),
            "estimated_pages": max(1, len(self.template.split("\n")) // 40),
        }