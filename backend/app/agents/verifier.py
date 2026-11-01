import logging
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field
from app.llm.base import BaseLLMProvider
from app.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class VerificationEvaluation(BaseModel):
    status: str = Field(description="'verified', 'partially_verified', 'conflicting', 'unsupported', or 'unverifiable'")
    confidence_score: float = Field(description="Score between 0.0 and 1.0 reflecting corroboration and credibility")
    supporting_indices: List[int] = Field(default=[], description="Indices of evidence snippets that confirm the claim")
    contradicting_indices: List[int] = Field(default=[], description="Indices of evidence snippets that contradict the claim")
    reasoning_summary: str = Field(description="Succinct justification of findings")
    conflict_details: Optional[str] = Field(default=None, description="Detailed explanation if conflicting sources detected")


def calculate_objective_confidence(
    num_supporting: int,
    num_contradicting: int,
    avg_credibility: float,
    status: str
) -> Tuple[float, str]:
    """
    Calculates an objective, transparent confidence score based on corroboration count,
    credibility of sources, and absence of conflicts (Section 17).
    """
    if status == "conflicting" or num_contradicting > 0:
        raw_score = 0.50 * avg_credibility
    elif status == "unsupported":
        raw_score = 0.15
    elif status == "unverifiable":
        raw_score = 0.20
    elif num_supporting >= 3:
        raw_score = min(0.98, 0.85 + 0.15 * avg_credibility)
    elif num_supporting == 2:
        raw_score = min(0.92, 0.75 + 0.20 * avg_credibility)
    elif num_supporting == 1:
        raw_score = min(0.80, 0.60 + 0.20 * avg_credibility)
    else:
        raw_score = 0.30

    final_score = round(max(0.0, min(1.0, raw_score)), 2)

    # Map to confidence tiers
    pct = final_score * 100.0
    if pct >= 90:
        tier = "Very High"
    elif pct >= 75:
        tier = "High"
    elif pct >= 50:
        tier = "Medium"
    elif pct >= 25:
        tier = "Low"
    else:
        tier = "Very Low"

    return final_score, tier


class FactVerificationAgent:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    def verify_claim(
        self,
        claim_text: str,
        claim_type: str,
        evidence_items: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Cross-checks an individual claim against available evidence.
        Returns: (verification_result, usage)
        """
        if not evidence_items:
            return {
                "claim_text": claim_text,
                "status": "unsupported",
                "confidence_score": 0.10,
                "confidence_tier": "Very Low",
                "reasoning_summary": "No supporting evidence retrieved.",
                "supporting_evidence": [],
                "contradicting_evidence": [],
                "conflicting_notes": None,
            }, {"input_tokens": 0, "output_tokens": 0, "model": "none"}

        # Format evidence items for prompt
        ev_strings = []
        for idx, ev in enumerate(evidence_items):
            ev_strings.append(
                f"[{idx}] Source: {ev.get('source_title', 'Source')} ({ev.get('domain', 'web')}) | Credibility: {ev.get('credibility_score', 0.7)}\n"
                f"Snippet: {ev.get('snippet', '')}"
            )
        formatted_evidence = "\n\n".join(ev_strings)

        prompt = load_prompt(
            "verifier",
            claim_text=claim_text,
            claim_type=claim_type,
            evidence_items=formatted_evidence
        )

        evaluation, usage = self.llm.generate_structured(
            prompt=prompt,
            pydantic_class=VerificationEvaluation,
            system_prompt="You are a strict, objective fact verification agent who never overlooks contradictions."
        )

        supporting_ev = [evidence_items[i] for i in evaluation.supporting_indices if 0 <= i < len(evidence_items)]
        contradicting_ev = [evidence_items[i] for i in evaluation.contradicting_indices if 0 <= i < len(evidence_items)]

        # If LLM didn't catch indices, fallback to provided evidence
        if not supporting_ev and not contradicting_ev and evidence_items:
            supporting_ev = [evidence_items[0]]

        # Calculate average credibility of supporting sources
        cred_list = [float(e.get("credibility_score", 0.70)) for e in supporting_ev] or [0.70]
        avg_cred = sum(cred_list) / len(cred_list)

        # Objective confidence calculation
        status = evaluation.status.lower()
        if contradicting_ev and status != "conflicting":
            status = "conflicting"

        conf_score, tier = calculate_objective_confidence(
            num_supporting=len(supporting_ev),
            num_contradicting=len(contradicting_ev),
            avg_credibility=avg_cred,
            status=status
        )

        conflict_notes = evaluation.conflict_details
        if status == "conflicting" and not conflict_notes:
            src_a = supporting_ev[0].get("source_title", "Source A") if supporting_ev else "Source A"
            src_b = contradicting_ev[0].get("source_title", "Source B") if contradicting_ev else "Source B"
            conflict_notes = f"CONFLICT DETECTED: Sources '{src_a}' and '{src_b}' present conflicting details for this claim."

        return {
            "claim_text": claim_text,
            "status": status,
            "confidence_score": conf_score,
            "confidence_tier": tier,
            "reasoning_summary": evaluation.reasoning_summary,
            "supporting_evidence": supporting_ev,
            "contradicting_evidence": contradicting_ev,
            "conflicting_notes": conflict_notes,
        }, usage
