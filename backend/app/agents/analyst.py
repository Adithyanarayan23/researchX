import logging
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from app.llm.base import BaseLLMProvider
from app.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class FindingItem(BaseModel):
    title: str = Field(description="Succinct title of the synthesized finding")
    statement: str = Field(description="Detailed finding statement")
    category: str = Field(description="'FACT', 'INFERENCE', or 'SPECULATION'")
    confidence_score: float = Field(description="Confidence between 0.0 and 1.0")
    confidence_tier: str = Field(description="'Very High', 'High', 'Medium', 'Low', 'Very Low'")
    evidence_count: int = Field(default=1, description="Number of supporting evidence points")


class AnalystSynthesis(BaseModel):
    findings: List[FindingItem] = Field(default=[])
    trends: List[str] = Field(default=[])
    opportunities: List[str] = Field(default=[])
    risks: List[str] = Field(default=[])
    unanswered_questions: List[str] = Field(default=[])


class ResearchAnalystAgent:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    def analyze_findings(
        self,
        research_question: str,
        verified_claims: List[Dict[str, Any]],
    ) -> Tuple[AnalystSynthesis, Dict[str, Any]]:
        """
        Synthesizes verified claims into structured findings distinguishing
        FACT, INFERENCE, and SPECULATION.
        """
        claims_summary_lines = []
        for idx, c in enumerate(verified_claims):
            status = c.get("status", "verified")
            conf = c.get("confidence_score", 0.8)
            tier = c.get("confidence_tier", "High")
            claims_summary_lines.append(
                f"- [{status.upper()} | {tier} ({conf})] {c.get('claim_text')}"
            )
        claims_summary = "\n".join(claims_summary_lines) or "No verified claims available."

        prompt = load_prompt(
            "analyst",
            research_question=research_question,
            verified_claims_summary=claims_summary
        )

        logger.info("ResearchAnalystAgent synthesizing %d claims", len(verified_claims))
        synthesis, usage = self.llm.generate_structured(
            prompt=prompt,
            pydantic_class=AnalystSynthesis,
            system_prompt="You are a senior research analyst who rigorously categorizes insights into FACT, INFERENCE, and SPECULATION."
        )

        return synthesis, usage
