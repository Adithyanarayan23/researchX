import re
import logging
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from app.llm.base import BaseLLMProvider
from app.services.prompt_loader import load_prompt
from app.core.config import settings

logger = logging.getLogger(__name__)


class QualityAssessmentResult(BaseModel):
    quality_score: float = Field(description="Score between 0.0 and 100.0 evaluating factual grounding and structure")
    passed: bool = Field(description="True if quality_score >= threshold, else False")
    is_hallucination_detected: bool = Field(default=False)
    citation_coverage_pct: float = Field(default=90.0, description="Percentage of claims properly cited")
    feedback: str = Field(description="Detailed critique and recommended revisions if any")
    unsupported_claims: List[str] = Field(default=[], description="List of any uncited or questionable assertions")


class QualityControlAgent:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm
        self.threshold = settings.QC_SCORE_THRESHOLD

    def evaluate_report(
        self,
        draft_report: str,
        research_question: str,
        citations: List[Dict[str, Any]],
    ) -> Tuple[QualityAssessmentResult, Dict[str, Any]]:
        """
        Critiques drafted report against citation accuracy, hallucination detection,
        and answer completeness.
        """
        # Formulate list of allowed citations
        citations_text_lines = []
        for c in citations:
            citations_text_lines.append(f"[{c['citation_number']}] {c.get('source_title')} ({c.get('source_url')})")
        citations_text = "\n".join(citations_text_lines) or "No citations indexed."

        prompt = load_prompt(
            "quality_checker",
            draft_report=draft_report,
            research_question=research_question,
            available_citations=citations_text,
            qc_threshold=self.threshold
        )

        logger.info("QualityControlAgent evaluating report quality against threshold %s", self.threshold)
        assessment, usage = self.llm.generate_structured(
            prompt=prompt,
            pydantic_class=QualityAssessmentResult,
            system_prompt="You are an uncompromising editorial quality auditor. You reject reports with hallucinated claims or broken citations."
        )

        # Enforce threshold logic
        if assessment.quality_score < self.threshold:
            assessment.passed = False
        else:
            assessment.passed = True

        return assessment, usage
