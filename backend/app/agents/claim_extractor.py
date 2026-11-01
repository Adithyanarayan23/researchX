import logging
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from app.llm.base import BaseLLMProvider
from app.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class ExtractedClaimItem(BaseModel):
    claim_text: str = Field(description="The atomic factual statement extracted from evidence")
    claim_type: str = Field(default="general", description="financial, technical, market, company, statistical, historical, competitive, general")
    importance: str = Field(default="medium", description="high, medium, low")
    evidence_indices: List[int] = Field(default=[], description="Zero-based indices of evidence snippets that support this claim")


class ExtractedClaimsPayload(BaseModel):
    claims: List[ExtractedClaimItem] = Field(default=[])


class ClaimExtractionAgent:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    def extract_claims(
        self,
        evidence_items: List[Dict[str, Any]],
        max_claims: int = 15
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extracts atomic factual claims from aggregated evidence items.
        Returns: (claims_list, usage)
        """
        if not evidence_items:
            logger.warning("No evidence provided to ClaimExtractionAgent")
            return [], {"input_tokens": 0, "output_tokens": 0, "model": "none"}

        # Format numbered evidence list for prompt
        evidence_text_lines = []
        for idx, ev in enumerate(evidence_items):
            evidence_text_lines.append(
                f"[{idx}] Source: {ev.get('source_title', 'Source')} ({ev.get('domain', 'web')})\n"
                f"Content: {ev.get('snippet', '')}"
            )
        formatted_evidence = "\n\n".join(evidence_text_lines)

        prompt = load_prompt(
            "claim_extractor",
            evidence_text=formatted_evidence
        )

        logger.info("ClaimExtractionAgent analyzing %d evidence snippets", len(evidence_items))
        payload, usage = self.llm.generate_structured(
            prompt=prompt,
            pydantic_class=ExtractedClaimsPayload,
            system_prompt="You are a precise fact extraction agent who isolates verifiable statements with references."
        )

        claims_result = []
        for c in payload.claims[:max_claims]:
            linked_evidence = []
            for ev_idx in c.evidence_indices:
                if 0 <= ev_idx < len(evidence_items):
                    linked_evidence.append(evidence_items[ev_idx])

            claims_result.append({
                "claim_text": c.claim_text,
                "claim_type": c.claim_type,
                "importance": c.importance,
                "evidence": linked_evidence if linked_evidence else [evidence_items[0]],
            })

        return claims_result, usage
