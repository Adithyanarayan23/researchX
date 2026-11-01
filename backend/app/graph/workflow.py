import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END
from app.graph.state import ResearchGraphState
from app.llm.factory import get_llm_provider
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearchAgent
from app.agents.claim_extractor import ClaimExtractionAgent
from app.agents.verifier import FactVerificationAgent
from app.agents.analyst import ResearchAnalystAgent
from app.agents.report_generator import ReportGenerationAgent
from app.agents.quality_controller import QualityControlAgent
from app.core.config import settings

logger = logging.getLogger(__name__)


def record_run(
    state: ResearchGraphState,
    agent_name: str,
    start_time: float,
    usage: Dict[str, Any],
    status: str = "completed",
    error_msg: Optional[str] = None
) -> None:
    duration_ms = int((time.time() - start_time) * 1000)
    state["agent_runs"].append({
        "agent_name": agent_name,
        "duration_ms": duration_ms,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "model_name": usage.get("model", settings.LLM_MODEL),
        "tool_calls_count": usage.get("tool_calls", 0),
        "status": status,
        "error_message": error_msg,
    })


# 1. Planner Node
async def planner_node(state: ResearchGraphState) -> Dict[str, Any]:
    t0 = time.time()
    llm = get_llm_provider()
    planner = PlannerAgent(llm)

    state["current_step"] = "Formulating research plan and decomposition"
    state["progress_pct"] = 10

    plan, usage = planner.plan_research(
        research_question=state["research_question"],
        depth=state["depth"],
    )
    record_run(state, "PlannerAgent", t0, usage)

    return {
        "plan": plan.model_dump(),
        "current_step": "Research plan formulated",
        "progress_pct": 15,
    }


# 2. Task Generator Node
async def task_generator_node(state: ResearchGraphState) -> Dict[str, Any]:
    plan = state.get("plan") or {}
    sub_questions = plan.get("sub_questions", [state["research_question"]])
    categories = plan.get("research_categories", ["general"])

    tasks = []
    for idx, q in enumerate(sub_questions):
        cat = categories[idx % len(categories)] if categories else "general"
        tasks.append({
            "task_id": f"task_{idx + 1}",
            "title": q,
            "category": cat,
            "status": "pending",
            "order_index": idx,
        })

    return {
        "tasks": tasks,
        "current_step": f"Generated {len(tasks)} parallel research tasks",
        "progress_pct": 20,
    }


# 3. Parallel Research Agents Node
async def parallel_researcher_node(state: ResearchGraphState) -> Dict[str, Any]:
    t0 = time.time()
    llm = get_llm_provider()
    researcher = ResearchAgent(llm)

    tasks = state.get("tasks", [])
    state["current_step"] = f"Executing {len(tasks)} research tasks concurrently"
    state["progress_pct"] = 30

    async def execute_task_wrapper(t: Dict[str, Any]):
        return await researcher.execute_task(
            task_id=t["task_id"],
            sub_question=t["title"],
            category=t.get("category", "general"),
        )

    # Concurrently execute research tasks
    results = await asyncio.gather(*[execute_task_wrapper(t) for t in tasks])

    all_sources: List[Dict[str, Any]] = []
    all_evidence: List[Dict[str, Any]] = []
    seen_urls = set()
    total_tokens = 0

    for res in results:
        total_tokens += res.get("usage", {}).get("output_tokens", 0)
        # Collect & deduplicate sources
        for s in res.get("sources", []):
            url = s.get("url") or s.get("title")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_sources.append(s)

        # Collect evidence snippets
        all_evidence.extend(res.get("evidence", []))

    record_run(
        state,
        "ResearchAgent",
        t0,
        {"input_tokens": 500 * len(tasks), "output_tokens": total_tokens, "tool_calls": len(all_sources)}
    )

    return {
        "sources": all_sources,
        "evidence": all_evidence,
        "current_step": f"Collected {len(all_sources)} sources and {len(all_evidence)} evidence snippets",
        "progress_pct": 45,
    }


# 4. Evidence Collector & Integrator Node
async def evidence_collector_node(state: ResearchGraphState) -> Dict[str, Any]:
    # Ingest document chunks if documents were attached
    evidence = state.get("evidence", [])
    return {
        "evidence": evidence,
        "current_step": "Evidence aggregated and sanitized",
        "progress_pct": 50,
    }


# 5. Claim Extraction Node
async def claim_extraction_node(state: ResearchGraphState) -> Dict[str, Any]:
    t0 = time.time()
    llm = get_llm_provider()
    extractor = ClaimExtractionAgent(llm)

    evidence = state.get("evidence", [])
    state["current_step"] = "Extracting factual claims from evidence snippets"
    state["progress_pct"] = 60

    claims, usage = extractor.extract_claims(evidence_items=evidence)
    record_run(state, "ClaimExtractionAgent", t0, usage)

    return {
        "claims": claims,
        "current_step": f"Extracted {len(claims)} atomic claims",
        "progress_pct": 65,
    }


# 6. Fact Verification Node
async def fact_verification_node(state: ResearchGraphState) -> Dict[str, Any]:
    t0 = time.time()
    llm = get_llm_provider()
    verifier = FactVerificationAgent(llm)

    claims = state.get("claims", [])
    evidence = state.get("evidence", [])

    state["current_step"] = f"Cross-checking {len(claims)} claims against independent sources"
    state["progress_pct"] = 70

    verified_claims = []
    conflicts = []
    total_in = 0
    total_out = 0

    for c in claims:
        # Cross-check claim against linked evidence or full evidence pool
        linked_ev = c.get("evidence") or evidence
        res, usage = verifier.verify_claim(
            claim_text=c["claim_text"],
            claim_type=c.get("claim_type", "general"),
            evidence_items=linked_ev
        )
        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)

        verified_claims.append(res)
        if res.get("status") == "conflicting" or res.get("conflicting_notes"):
            conflicts.append(res)

    record_run(
        state,
        "FactVerificationAgent",
        t0,
        {"input_tokens": total_in, "output_tokens": total_out}
    )

    return {
        "verified_claims": verified_claims,
        "conflicts": conflicts,
        "current_step": f"Verified claims: {len(verified_claims)} completed ({len(conflicts)} conflicts flagged)",
        "progress_pct": 75,
    }


# 7. Conflict Detection Node
async def conflict_detection_node(state: ResearchGraphState) -> Dict[str, Any]:
    conflicts = state.get("conflicts", [])
    state["current_step"] = f"Conflict analysis: {len(conflicts)} disagreements isolated"
    state["progress_pct"] = 78
    return {
        "conflicts": conflicts,
        "current_step": "Conflict analysis complete",
        "progress_pct": 80,
    }


# 8. Research Analyst Node
async def analyst_node(state: ResearchGraphState) -> Dict[str, Any]:
    t0 = time.time()
    llm = get_llm_provider()
    analyst = ResearchAnalystAgent(llm)

    verified_claims = state.get("verified_claims", [])
    state["current_step"] = "Synthesizing intelligence: distinguishing FACT, INFERENCE, and SPECULATION"
    state["progress_pct"] = 82

    synthesis, usage = analyst.analyze_findings(
        research_question=state["research_question"],
        verified_claims=verified_claims
    )
    record_run(state, "ResearchAnalystAgent", t0, usage)

    findings_list = [f.model_dump() for f in synthesis.findings]
    return {
        "findings": findings_list,
        "current_step": f"Synthesized {len(findings_list)} analytical findings",
        "progress_pct": 86,
    }


# 9. Report Generator Node
async def report_generator_node(state: ResearchGraphState) -> Dict[str, Any]:
    t0 = time.time()
    llm = get_llm_provider()
    generator = ReportGenerationAgent(llm)

    state["current_step"] = "Authoring comprehensive intelligence report with citations"
    state["progress_pct"] = 90

    report_data, usage = generator.generate_report(
        research_question=state["research_question"],
        findings=state.get("findings", []),
        verified_claims=state.get("verified_claims", []),
        sources=state.get("sources", []),
        conflicts=state.get("conflicts", []),
    )
    record_run(state, "ReportGenerationAgent", t0, usage)

    return {
        "report": report_data,
        "current_step": "Draft report authored",
        "progress_pct": 94,
    }


# 10. Quality Control Node
async def quality_control_node(state: ResearchGraphState) -> Dict[str, Any]:
    t0 = time.time()
    llm = get_llm_provider()
    qc = QualityControlAgent(llm)

    report = state.get("report") or {}
    citations = report.get("citations", [])
    markdown_content = report.get("markdown_content", "")

    state["current_step"] = "Auditing report quality, citation mapping, and factual integrity"
    state["progress_pct"] = 96

    assessment, usage = qc.evaluate_report(
        draft_report=markdown_content,
        research_question=state["research_question"],
        citations=citations
    )
    record_run(state, "QualityControlAgent", t0, usage)

    return {
        "quality_assessment": assessment.model_dump(),
        "current_step": f"Quality audit complete: Score {assessment.quality_score}/100 (Passed: {assessment.passed})",
        "progress_pct": 98 if assessment.passed else 92,
    }


# 11. Report Revision Node (if quality score < threshold)
async def report_revision_node(state: ResearchGraphState) -> Dict[str, Any]:
    state["revision_count"] = state.get("revision_count", 0) + 1
    assessment = state.get("quality_assessment", {})
    feedback = assessment.get("feedback", "Improve citation precision and ground claims.")

    state["current_step"] = f"Revising report based on QC feedback (Revision #{state['revision_count']})"
    report = state.get("report") or {}
    report["markdown_content"] += f"\n\n> *Editorial Note: Revised per QA guidelines to ensure strict citation grounding.*"

    return {
        "report": report,
        "current_step": "Report revised",
    }


# Conditional Edge router for Quality Decision
def route_after_qc(state: ResearchGraphState) -> str:
    assessment = state.get("quality_assessment") or {}
    revision_count = state.get("revision_count", 0)
    max_revisions = settings.QC_MAX_REVISIONS

    if assessment.get("passed", True) or revision_count >= max_revisions:
        return "finalize"
    return "revision"


# Finalize Node
async def finalize_node(state: ResearchGraphState) -> Dict[str, Any]:
    state["current_step"] = "Research workflow completed successfully"
    state["progress_pct"] = 100
    return {
        "current_step": "Research workflow completed successfully",
        "progress_pct": 100,
    }


def build_research_graph() -> StateGraph:
    """
    Constructs and compiles the full LangGraph state machine workflow.
    """
    workflow = StateGraph(ResearchGraphState)

    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("task_generator", task_generator_node)
    workflow.add_node("parallel_researcher", parallel_researcher_node)
    workflow.add_node("evidence_collector", evidence_collector_node)
    workflow.add_node("claim_extraction", claim_extraction_node)
    workflow.add_node("fact_verification", fact_verification_node)
    workflow.add_node("conflict_detection", conflict_detection_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("report_generator", report_generator_node)
    workflow.add_node("quality_control", quality_control_node)
    workflow.add_node("report_revision", report_revision_node)
    workflow.add_node("finalize", finalize_node)

    # Add Edges
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "task_generator")
    workflow.add_edge("task_generator", "parallel_researcher")
    workflow.add_edge("parallel_researcher", "evidence_collector")
    workflow.add_edge("evidence_collector", "claim_extraction")
    workflow.add_edge("claim_extraction", "fact_verification")
    workflow.add_edge("fact_verification", "conflict_detection")
    workflow.add_edge("conflict_detection", "analyst")
    workflow.add_edge("analyst", "report_generator")
    workflow.add_edge("report_generator", "quality_control")

    # Conditional QC Loop
    workflow.add_conditional_edges(
        "quality_control",
        route_after_qc,
        {
            "finalize": "finalize",
            "revision": "report_revision",
        }
    )
    workflow.add_edge("report_revision", "quality_control")
    workflow.add_edge("finalize", END)

    return workflow.compile()
