import pytest
import asyncio
from app.graph.workflow import build_research_graph
from app.graph.state import ResearchGraphState


def test_full_system_e2e_research_flow():
    """
    End-to-end test verifying complete multi-agent LangGraph workflow execution:
    Planner -> Task Generator -> Parallel Researchers -> Evidence Collector ->
    Claim Extraction -> Fact Verification -> Conflict Detection -> Analyst ->
    Report Generator -> Quality Control -> Citations.
    """
    async def _run():
        query = "Compare OpenAI, Google DeepMind and Anthropic in the AI model market."

        initial_state: ResearchGraphState = {
            "job_id": "test_job_e2e_001",
            "research_question": query,
            "depth": "standard",
            "document_ids": None,
            "plan": None,
            "tasks": [],
            "sources": [],
            "evidence": [],
            "claims": [],
            "verified_claims": [],
            "conflicts": [],
            "findings": [],
            "report": None,
            "quality_assessment": None,
            "revision_count": 0,
            "current_step": "Initializing E2E test",
            "progress_pct": 0,
            "agent_runs": [],
            "error": None,
        }

        graph = build_research_graph()
        final_state = await graph.ainvoke(initial_state)

        # 1. Verify Planner
        assert final_state["plan"] is not None
        assert len(final_state["plan"]["sub_questions"]) >= 3

        # 2. Verify Tasks
        assert len(final_state["tasks"]) >= 3

        # 3. Verify Sources
        assert len(final_state["sources"]) > 0

        # 4. Verify Claims Extracted
        assert len(final_state["claims"]) > 0

        # 5. Verify Claims Verified & Scored
        assert len(final_state["verified_claims"]) > 0
        first_claim = final_state["verified_claims"][0]
        assert "status" in first_claim
        assert "confidence_score" in first_claim

        # 6. Verify Analyst Findings (FACT / INFERENCE / SPECULATION)
        assert len(final_state["findings"]) > 0
        categories = {f["category"] for f in final_state["findings"]}
        assert any(cat in categories for cat in ("FACT", "INFERENCE", "SPECULATION"))

        # 7. Verify Report Generated with Citations
        assert final_state["report"] is not None
        report_content = final_state["report"]["markdown_content"]
        assert "# Executive Summary" in report_content
        assert "# Key Findings" in report_content
        assert "# Methodology" in report_content
        assert len(final_state["report"]["citations"]) > 0

        # 8. Verify Quality Control
        assert final_state["quality_assessment"] is not None
        assert final_state["quality_assessment"]["quality_score"] > 70.0

    asyncio.run(_run())
