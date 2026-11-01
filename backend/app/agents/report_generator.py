import re
import logging
from typing import List, Dict, Any, Tuple
from app.llm.base import BaseLLMProvider
from app.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class ReportGenerationAgent:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    def generate_report(
        self,
        research_question: str,
        findings: List[Dict[str, Any]],
        verified_claims: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Compiles the structured publication-grade research report with embedded
        and verified footnote citations.
        """
        # Deduplicate and index sources to create stable [1], [2] citations
        indexed_sources = []
        source_url_map = {}
        for s in sources:
            url = s.get("url") or s.get("title", "")
            if url not in source_url_map:
                source_url_map[url] = len(indexed_sources) + 1
                indexed_sources.append({
                    "citation_number": len(indexed_sources) + 1,
                    "title": s.get("title", "Research Source"),
                    "url": s.get("url", ""),
                    "domain": s.get("domain", "web"),
                    "source_id": s.get("id"),
                    "credibility_score": s.get("credibility_score", 0.75),
                    "snippet": s.get("content", "")[:300] if s.get("content") else ""
                })

        # Format citations & claims for prompt
        claims_with_citations = []
        for c in verified_claims:
            claim_text = c.get("claim_text", "")
            supp = c.get("supporting_evidence", [])
            cit_nums = []
            for ev in supp:
                u = ev.get("source_url") or ev.get("source_title", "")
                if u in source_url_map:
                    cit_nums.append(f"[{source_url_map[u]}]")
            cit_str = "".join(set(cit_nums)) if cit_nums else "[1]"
            claims_with_citations.append(f"- {claim_text} {cit_str}")

        citations_and_claims_text = "\n".join(claims_with_citations)

        # Format findings summary
        findings_summary_lines = []
        for f in findings:
            findings_summary_lines.append(
                f"- [{f.get('category', 'FACT')}] {f.get('title')}: {f.get('statement')} (Confidence: {f.get('confidence_tier')})"
            )
        findings_summary_text = "\n".join(findings_summary_lines)

        # Format conflicts summary
        conflicts_text = "\n".join([f"- {c.get('conflicting_notes')}" for c in conflicts if c.get("conflicting_notes")])
        if not conflicts_text:
            conflicts_text = "No material conflicting data points observed across evaluated independent sources."

        prompt = load_prompt(
            "report_generator",
            research_question=research_question,
            findings_summary=findings_summary_text or "General findings synthesized.",
            citations_and_claims=citations_and_claims_text or "Primary claims validated.",
            conflict_summary=conflicts_text
        )

        logger.info("ReportGenerationAgent authoring report for query: '%s'", research_question)
        markdown_body, usage = self.llm.generate_text(
            prompt=prompt,
            system_prompt="You are an elite principal research analyst. You author publication-grade reports with clean markdown tables and rigorous citation footnotes.",
            temperature=0.2,
            max_tokens=4096
        )

        # Extract executive summary snippet
        exec_summary = ""
        match = re.search(r"# Executive Summary\s*\n+([^#]+)", markdown_body)
        if match:
            exec_summary = match.group(1).strip()
        else:
            exec_summary = markdown_body[:300].strip()

        # Build citation objects that map to the report
        final_citations = []
        for s in indexed_sources:
            final_citations.append({
                "citation_number": s["citation_number"],
                "source_id": s.get("source_id"),
                "source_title": s["title"],
                "source_url": s["url"],
                "source_domain": s["domain"],
                "snippet": s["snippet"]
            })

        report_data = {
            "title": f"Intelligence Analysis: {research_question[:80]}",
            "executive_summary": exec_summary,
            "markdown_content": markdown_body,
            "citations": final_citations,
            "sources": indexed_sources,
        }

        return report_data, usage
