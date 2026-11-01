import asyncio
import json
import logging
from typing import List, Dict, Any
from evaluation.metrics.retrieval_metrics import precision_at_k, recall_at_k
from evaluation.metrics.rag_metrics import context_relevance, context_completeness, faithfulness
from evaluation.metrics.claim_metrics import claim_support_rate, unsupported_claim_rate, citation_accuracy
from evaluation.metrics.research_metrics import source_diversity, source_quality, conflict_detection_rate
from app.graph.workflow import build_research_graph
from app.graph.state import ResearchGraphState

logger = logging.getLogger(__name__)


class ResearchXEvaluator:
    def __init__(self, benchmark_path: str):
        with open(benchmark_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)
        self.graph = build_research_graph()

    async def evaluate_sample(self, item: Dict[str, Any]) -> Dict[str, Any]:
        question = item["question"]
        expected_entities = item.get("expected_entities", [])
        expected_topics = item.get("expected_topics", [])
        expected_conflict = item.get("has_conflict", False)

        initial_state: ResearchGraphState = {
            "job_id": f"eval_{item['id']}",
            "research_question": question,
            "depth": "quick",
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
            "current_step": "Starting evaluation run",
            "progress_pct": 0,
            "agent_runs": [],
            "error": None,
        }

        # Run state machine
        final_state = await self.graph.ainvoke(initial_state)

        evidence_snippets = [e.get("snippet", "") for e in final_state.get("evidence", [])]
        sources = final_state.get("sources", [])
        claims = final_state.get("verified_claims", [])
        conflicts = final_state.get("conflicts", [])
        report = final_state.get("report") or {}
        markdown_body = report.get("markdown_content", "")

        # Compute Metrics
        p_at_k = precision_at_k(evidence_snippets, expected_entities, k=3)
        r_at_k = recall_at_k(evidence_snippets, expected_entities, k=5)
        ctx_rel = context_relevance(question, evidence_snippets)
        ctx_comp = context_completeness(expected_topics, evidence_snippets)
        faith = faithfulness(claims, evidence_snippets)
        supp_rate = claim_support_rate(claims)
        unsupp_rate = unsupported_claim_rate(claims)
        cit_acc = citation_accuracy(markdown_body, sources)
        src_div = source_diversity(sources)
        src_qual = source_quality(sources)
        conf_rate = conflict_detection_rate(conflicts, expected_conflict)

        return {
            "id": item["id"],
            "question": question,
            "metrics": {
                "precision_at_3": p_at_k,
                "recall_at_5": r_at_k,
                "context_relevance": ctx_rel,
                "context_completeness": ctx_comp,
                "faithfulness": faith,
                "claim_support_rate": supp_rate,
                "unsupported_claim_rate": unsupp_rate,
                "citation_accuracy": cit_acc,
                "source_diversity": src_div,
                "source_quality": src_qual,
                "conflict_detection_rate": conf_rate,
            }
        }

    async def run_benchmark(self, limit: int = 20) -> Dict[str, Any]:
        results = []
        samples = self.dataset[:limit]

        for idx, item in enumerate(samples):
            logger.info("Evaluating [%d/%d]: %s", idx + 1, len(samples), item["question"][:60])
            res = await self.evaluate_sample(item)
            results.append(res)

        # Aggregate averages
        agg_metrics: Dict[str, float] = {}
        first_keys = results[0]["metrics"].keys()
        for k in first_keys:
            vals = [r["metrics"][k] for r in results]
            agg_metrics[f"avg_{k}"] = round(sum(vals) / len(vals), 4)

        return {
            "total_evaluated": len(results),
            "aggregate_metrics": agg_metrics,
            "detailed_results": results,
        }
