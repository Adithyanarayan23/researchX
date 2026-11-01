import pytest
import asyncio
from app.llm.mock import MockLLMProvider
from app.agents.planner import PlannerAgent
from app.agents.claim_extractor import ClaimExtractionAgent
from app.agents.verifier import FactVerificationAgent
from app.agents.analyst import ResearchAnalystAgent
from app.agents.report_generator import ReportGenerationAgent
from app.agents.quality_controller import QualityControlAgent
from app.graph.workflow import build_research_graph
from app.graph.state import ResearchGraphState


def test_agent_pipeline_integration():
    async def _run():
        mock_llm = MockLLMProvider()

        # 1. Planner
        planner = PlannerAgent(mock_llm)
        plan, _ = planner.plan_research("Compare NVIDIA, AMD and Intel in AI accelerators")
        assert len(plan.sub_questions) >= 3
        assert plan.priority == "high"

        # 2. Claim Extraction
        extractor = ClaimExtractionAgent(mock_llm)
        mock_evidence = [
            {"source_title": "SemiAnalysis", "domain": "semianalysis.com", "snippet": "NVIDIA revenue reached $130.5 billion."},
            {"source_title": "AMD Disclosures", "domain": "amd.com", "snippet": "AMD Instinct MI300X offers 192GB memory."}
        ]
        claims, _ = extractor.extract_claims(mock_evidence)
        assert len(claims) > 0
        assert "claim_text" in claims[0]

        # 3. Verification
        verifier = FactVerificationAgent(mock_llm)
        res, _ = verifier.verify_claim(
            claim_text=claims[0]["claim_text"],
            claim_type="financial",
            evidence_items=mock_evidence
        )
        assert res["status"] in ("verified", "partially_verified", "conflicting")
        assert "confidence_score" in res

        # 4. Analyst
        analyst = ResearchAnalystAgent(mock_llm)
        synthesis, _ = analyst.analyze_findings("Compare NVIDIA, AMD and Intel", [res])
        assert len(synthesis.findings) >= 1
        assert synthesis.findings[0].category in ("FACT", "INFERENCE", "SPECULATION")

        # 5. Report Generator
        generator = ReportGenerationAgent(mock_llm)
        report_data, _ = generator.generate_report(
            research_question="Compare NVIDIA, AMD and Intel",
            findings=[f.model_dump() for f in synthesis.findings],
            verified_claims=[res],
            sources=mock_evidence,
            conflicts=[]
        )
        assert "markdown_content" in report_data
        assert "Executive Summary" in report_data["markdown_content"]
        assert len(report_data["citations"]) > 0

        # 6. Quality Control
        qc = QualityControlAgent(mock_llm)
        assessment, _ = qc.evaluate_report(
            draft_report=report_data["markdown_content"],
            research_question="Compare NVIDIA, AMD and Intel",
            citations=report_data["citations"]
        )
        assert assessment.quality_score >= 80.0
        assert assessment.passed is True

    asyncio.run(_run())
