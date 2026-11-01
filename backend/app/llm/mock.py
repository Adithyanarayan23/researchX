import hashlib
import json
import re
from typing import Type, TypeVar, Tuple, Dict, Any, Optional, List
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM provider for tests, local offline development, and evaluation.
    Synthesizes rich, domain-specific research responses without external API calls.
    """

    def __init__(self, model_name: str = "mock-agentic-v1"):
        self.model_name = model_name

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> Tuple[str, Dict[str, Any]]:
        prompt_lower = prompt.lower()
        topic = "the subject"
        if "compare" in prompt_lower or "market" in prompt_lower or "startup" in prompt_lower:
            match = re.search(r'["\']([^"\']+)["\']', prompt)
            if match:
                topic = match.group(1)
            else:
                topic = prompt.strip().split("\n")[0][:60]

        if "quality" in prompt_lower or "qc" in prompt_lower:
            text = (
                "## Quality Assessment\n\n"
                "The research report satisfies factual consistency and grounding requirements. "
                "Citations map accurately to retrieved sources. All major statistical claims are cross-checked."
            )
        elif "report" in prompt_lower:
            text = f"""# Executive Summary

This comprehensive intelligence report analyzes **{topic}**. Across evaluated market segments, accelerated adoption and capital consolidation characterize the current landscape. Key competitors maintain differentiated technical moats, while regulatory and infrastructure bottlenecks pose near-term friction.

# Research Question
{topic}

# Methodology
- **Multi-Agent Retrieval**: Parallel collection across vetted industry publications, SEC/company filings, and technical documentation.
- **Fact Verification**: Multi-source corroboration with cross-checking algorithms.
- **Classification**: Separation into verifiable facts, reasoned inferences, and monitored speculation.

# Key Findings
1. **Consolidated Infrastructure Spend**: Enterprise investments have grown over 40% year-over-year [1].
2. **Specialized Architecture Moats**: Custom silicon and domain-tuned architectures yield a 3.2x inference efficiency advantage [2].
3. **Ecosystem Lock-In**: Software tooling and developer ecosystems remain the primary barrier to competitive disruption [1].
4. **Capital Reallocation**: Growth funding is increasingly concentrated into top-quartile platforms [3].

# Detailed Analysis

## Market Dynamics & Product Architecture
The market demonstrates rapid divergence between general-purpose infrastructure and vertically integrated domain platforms. Market leaders continue to expand platform coverage, achieving substantial margin expansion through recurring high-value workload deployment [1].

| Parameter | Market Leader | Challengers | Open/Alternative |
|---|---|---|---|
| Adoption Pace | Dominant Enterprise Footprint | Rapid Growth in Mid-Market | Fast Academic / OSS Uptake |
| Margin Profile | 65% - 78% Gross Margin | 45% - 60% Gross Margin | Variable / Community-driven |
| Core Advantage | Deep Software Moat & Tooling | Aggressive Price-to-Performance | Customizability & Data Privacy |

## Trends
1. Transition from monolithic architectures to compound agent workflows [2].
2. Focus on token efficiency, localized inference, and predictable latency profiles [1].

## Opportunities
- Addressing enterprise security, auditability, and guardrail requirements.
- Hybrid deployment topologies combining edge devices and private clouds [3].

## Risks
- Upstream supply-chain constraints and energy grid limitations.
- Regulatory compliance mandates regarding automated decision systems.

## Conflicting Information
Discrepancies were observed between self-reported enterprise ARR metrics and independent audited market assessments. Independent third-party estimates place growth at 34%, whereas primary corporate filings project up to 48% growth.

# Conclusion
The ecosystem is maturing rapidly from speculative experimentation into verifiable operational efficiency. Organizations maintaining proprietary data moats and robust tooling ecosystems are positioned to capture disproportionate enterprise value.

# Sources
- [1] Global Technology Market Report & Analysis (2025)
- [2] IEEE / ACM Architecture Review & Performance Benchmarks
- [3] Venture Industry Quarterly Financial Dispatch
"""
        else:
            text = f"Synthetic analysis regarding {topic}. Evaluated evidence confirms verifiable momentum across key sectors."

        usage = {
            "input_tokens": len(prompt.split()) + 25,
            "output_tokens": len(text.split()),
            "model": self.model_name,
        }
        return text, usage

    def generate_structured(
        self,
        prompt: str,
        pydantic_class: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> Tuple[T, Dict[str, Any]]:
        class_name = pydantic_class.__name__
        prompt_lower = prompt.lower()

        # Generate realistic mock data for each schema type
        if class_name == "ResearchPlan":
            # Extract main topic or entities from prompt
            sub_q = [
                "What is the current market sizing, revenue trajectory, and overall adoption rate?",
                "Who are the key architectural leaders, flagship offerings, and technical benchmarks?",
                "What are the major structural competitive advantages and ecosystem barriers?",
                "What are the principal supply chain, technological, or regulatory risks?",
            ]
            cats = ["market", "technology", "competition", "financial", "risks"]
            sources = ["industry reports", "company filings", "technical whitepapers", "news"]

            data = {
                "research_goal": f"Execute in-depth competitive, technical, and market investigation of the user inquiry.",
                "sub_questions": sub_q,
                "research_categories": cats,
                "required_sources": sources,
                "priority": "high",
            }

        elif "Claim" in class_name:
            data = {
                "claims": [
                    {
                        "claim_text": "Enterprise AI infrastructure investment expanded by more than 40% year-over-year.",
                        "claim_type": "market",
                        "importance": "high",
                        "evidence_indices": [0],
                    },
                    {
                        "claim_text": "Proprietary software ecosystems represent the primary switching barrier for competing platforms.",
                        "claim_type": "competitive",
                        "importance": "high",
                        "evidence_indices": [0],
                    },
                    {
                        "claim_text": "Domain-specific architectures demonstrate an average 3.2x efficiency advantage over general-purpose equivalents.",
                        "claim_type": "technical",
                        "importance": "medium",
                        "evidence_indices": [0],
                    },
                ]
            }

        elif "Verification" in class_name:
            data = {
                "status": "verified",
                "confidence_score": 0.92,
                "supporting_indices": [0],
                "contradicting_indices": [],
                "reasoning_summary": "Corroborated across multiple independent industry reports and market disclosures.",
                "conflict_details": None,
            }

        elif "Analyst" in class_name or "Synthesis" in class_name:
            data = {
                "findings": [
                    {
                        "title": "Consolidated Infrastructure Capital Allocation",
                        "statement": "Enterprise investments in specialized AI acceleration have expanded over 40% year-over-year.",
                        "category": "FACT",
                        "confidence_score": 0.94,
                        "confidence_tier": "Very High",
                        "evidence_count": 3,
                    },
                    {
                        "title": "Software Moat as the Dominant Disruption Barrier",
                        "statement": "Ecosystem tooling maturity creates a significant switching barrier for enterprise workloads.",
                        "category": "INFERENCE",
                        "confidence_score": 0.88,
                        "confidence_tier": "High",
                        "evidence_count": 2,
                    },
                    {
                        "title": "Long-Term Energy Grid and Compute Constraints",
                        "statement": "Power availability and transmission capacity may cap cluster expansion velocity by 2027.",
                        "category": "SPECULATION",
                        "confidence_score": 0.62,
                        "confidence_tier": "Medium",
                        "evidence_count": 1,
                    },
                ],
                "trends": [
                    "Transition from standalone models to multi-agent compound systems",
                    "Rapid adoption of specialized domain accelerators",
                ],
                "opportunities": [
                    "Enterprise security, auditability, and guardrail platforms",
                    "Hybrid deployment topologies combining edge devices and private clouds",
                ],
                "risks": [
                    "Upstream silicon fabrication bottlenecks and geopolitical constraints",
                    "Regulatory compliance mandates regarding automated decision systems",
                ],
                "unanswered_questions": [
                    "Long-term margin stabilization for token-based APIs",
                ],
            }

        elif "Quality" in class_name or "Assessment" in class_name:
            data = {
                "quality_score": 92.5,
                "passed": True,
                "is_hallucination_detected": False,
                "citation_coverage_pct": 94.0,
                "feedback": "Report is cohesive, well-grounded, and thoroughly cited.",
                "unsupported_claims": [],
            }

        else:
            # Generic fallback mock matching fields from schema
            data = {}
            for field_name, field in pydantic_class.model_fields.items():
                annotation = str(field.annotation)
                if "str" in annotation:
                    data[field_name] = f"Sample {field_name}"
                elif "float" in annotation:
                    data[field_name] = 0.88
                elif "int" in annotation:
                    data[field_name] = 10
                elif "bool" in annotation:
                    data[field_name] = True
                elif "list" in annotation.lower():
                    data[field_name] = ["Item 1", "Item 2"]
                else:
                    data[field_name] = None

        instance = pydantic_class.model_validate(data)
        usage = {
            "input_tokens": len(prompt.split()) + 30,
            "output_tokens": 120,
            "model": self.model_name,
        }
        return instance, usage

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates a deterministic float vector based on SHA-256 hash of text.
        Consistent for cosine similarity calculations in tests and mock RAG!
        """
        dim = settings.EMBEDDING_DIMENSION
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Expand 32 bytes to dim floats in [-1.0, 1.0]
        floats = []
        for i in range(dim):
            byte_val = h[i % len(h)]
            # normalize to [-1.0, 1.0]
            val = (byte_val / 127.5) - 1.0
            floats.append(round(val, 4))
        return floats
