import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, AsyncGenerator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.research import (
    ResearchJob,
    ResearchTask,
    Source,
    Claim,
    ClaimEvidence,
    VerificationResult,
    Finding,
    Report,
    ReportCitation,
    AgentRun,
)
from app.graph.workflow import build_research_graph
from app.graph.state import ResearchGraphState

logger = logging.getLogger(__name__)

# In-memory pub/sub queues for SSE streaming per job_id
_JOB_EVENT_QUEUES: Dict[str, List[asyncio.Queue]] = {}


def register_job_listener(job_id: str) -> asyncio.Queue:
    queue = asyncio.Queue()
    if job_id not in _JOB_EVENT_QUEUES:
        _JOB_EVENT_QUEUES[job_id] = []
    _JOB_EVENT_QUEUES[job_id].append(queue)
    return queue


def unregister_job_listener(job_id: str, queue: asyncio.Queue) -> None:
    if job_id in _JOB_EVENT_QUEUES:
        if queue in _JOB_EVENT_QUEUES[job_id]:
            _JOB_EVENT_QUEUES[job_id].remove(queue)
        if not _JOB_EVENT_QUEUES[job_id]:
            del _JOB_EVENT_QUEUES[job_id]


async def broadcast_job_event(job_id: str, event_data: Dict[str, Any]) -> None:
    if job_id in _JOB_EVENT_QUEUES:
        for q in _JOB_EVENT_QUEUES[job_id]:
            await q.put(event_data)


async def execute_research_workflow(job_id: str) -> None:
    """
    Executes the full LangGraph research workflow, streaming progress events
    and persisting results to PostgreSQL / SQLite.
    """
    logger.info("Starting execution of research job: %s", job_id)

    db: Session = SessionLocal()
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if not job:
        logger.error("Job %s not found in database", job_id)
        db.close()
        return

    job.status = "planning"
    job.current_step = "Initializing multi-agent workflow"
    job.progress_pct = 5
    db.commit()

    await broadcast_job_event(job_id, {
        "status": job.status,
        "current_step": job.current_step,
        "progress_pct": job.progress_pct,
    })

    # Prepare initial LangGraph state
    initial_state: ResearchGraphState = {
        "job_id": job_id,
        "research_question": job.research_question,
        "depth": job.depth,
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
        "current_step": "Starting graph execution",
        "progress_pct": 5,
        "agent_runs": [],
        "error": None,
    }

    try:
        app_graph = build_research_graph()

        # Stream graph node transitions
        async for output in app_graph.astream(initial_state):
            for node_name, node_state in output.items():
                logger.info("Completed node %s for job %s", node_name, job_id)
                current_step = node_state.get("current_step", f"Completed {node_name}")
                progress_pct = node_state.get("progress_pct", job.progress_pct)

                # Map node names to status
                status_map = {
                    "planner": "planning",
                    "parallel_researcher": "researching",
                    "claim_extraction": "researching",
                    "fact_verification": "verifying",
                    "analyst": "analyzing",
                    "report_generator": "generating_report",
                    "quality_control": "generating_report",
                    "finalize": "completed",
                }
                new_status = status_map.get(node_name, job.status)

                job.status = new_status
                job.current_step = current_step
                job.progress_pct = progress_pct
                db.commit()

                # Broadcast live event
                await broadcast_job_event(job_id, {
                    "status": new_status,
                    "current_step": current_step,
                    "progress_pct": progress_pct,
                    "node": node_name,
                    "sources_count": len(node_state.get("sources", [])),
                    "claims_count": len(node_state.get("claims", [])),
                    "conflicts_count": len(node_state.get("conflicts", [])),
                })

                # Merge state for next iteration
                initial_state.update(node_state)

        # Persistence of final artifacts to database
        final_state = initial_state

        # 1. Save Tasks
        for t in final_state.get("tasks", []):
            task_record = ResearchTask(
                job_id=job_id,
                title=t["title"],
                category=t.get("category", "general"),
                status="completed",
                order_index=t.get("order_index", 0),
            )
            db.add(task_record)

        # 2. Save Sources
        source_id_map = {}
        for s in final_state.get("sources", []):
            src_record = Source(
                job_id=job_id,
                url=s.get("url"),
                title=s.get("title", "Untitled Source"),
                domain=s.get("domain"),
                publisher=s.get("publisher"),
                source_type=s.get("source_type", "website"),
                credibility_score=s.get("credibility_score", 0.70),
                content=s.get("content"),
                content_hash=s.get("content_hash"),
            )
            db.add(src_record)
            db.flush()
            if s.get("url"):
                source_id_map[s["url"]] = src_record.id

        # 3. Save Claims & Evidence & Verification
        for c in final_state.get("verified_claims", []):
            claim_rec = Claim(
                job_id=job_id,
                claim_text=c.get("claim_text", ""),
                claim_type="general",
                importance="high",
            )
            db.add(claim_rec)
            db.flush()

            # Save Verification
            verif_rec = VerificationResult(
                claim_id=claim_rec.id,
                status=c.get("status", "verified"),
                confidence_score=c.get("confidence_score", 0.85),
                reasoning_summary=c.get("reasoning_summary"),
                conflicting_notes=c.get("conflicting_notes"),
            )
            db.add(verif_rec)

            # Link evidence
            for ev in c.get("supporting_evidence", []):
                src_url = ev.get("source_url")
                src_id = source_id_map.get(src_url)
                if src_id:
                    ev_rec = ClaimEvidence(
                        claim_id=claim_rec.id,
                        source_id=src_id,
                        snippet=ev.get("snippet", ""),
                        relevance_score=1.0,
                        is_supporting=True,
                    )
                    db.add(ev_rec)

        # 4. Save Findings
        for idx, f in enumerate(final_state.get("findings", [])):
            find_rec = Finding(
                job_id=job_id,
                title=f.get("title", ""),
                statement=f.get("statement", ""),
                category=f.get("category", "FACT"),
                confidence_score=f.get("confidence_score", 0.85),
                confidence_tier=f.get("confidence_tier", "High"),
                evidence_count=f.get("evidence_count", 1),
                order_index=idx,
            )
            db.add(find_rec)

        # 5. Save Report & Citations
        rep_data = final_state.get("report")
        if rep_data:
            qc = final_state.get("quality_assessment") or {}
            rep_rec = Report(
                job_id=job_id,
                title=rep_data.get("title", f"Report: {job.title}"),
                executive_summary=rep_data.get("executive_summary", ""),
                markdown_content=rep_data.get("markdown_content", ""),
                quality_score=qc.get("quality_score", 90.0),
                revision_count=final_state.get("revision_count", 0),
                qc_notes=qc.get("feedback"),
            )
            db.add(rep_rec)
            db.flush()

            # Save Citations
            for cit in rep_data.get("citations", []):
                src_url = cit.get("source_url")
                src_id = source_id_map.get(src_url)
                if src_id:
                    cit_rec = ReportCitation(
                        report_id=rep_rec.id,
                        source_id=src_id,
                        citation_number=cit["citation_number"],
                        snippet=cit.get("snippet"),
                    )
                    db.add(cit_rec)

        # 6. Save Agent Runs
        for run in final_state.get("agent_runs", []):
            run_rec = AgentRun(
                job_id=job_id,
                agent_name=run["agent_name"],
                duration_ms=run.get("duration_ms", 0),
                input_tokens=run.get("input_tokens", 0),
                output_tokens=run.get("output_tokens", 0),
                model_name=run.get("model_name"),
                tool_calls_count=run.get("tool_calls_count", 0),
                status=run.get("status", "completed"),
                error_message=run.get("error_message"),
            )
            db.add(run_rec)

        job.status = "completed"
        job.progress_pct = 100
        job.current_step = "Research and intelligence analysis completed."
        db.commit()

        await broadcast_job_event(job_id, {
            "status": "completed",
            "progress_pct": 100,
            "current_step": job.current_step,
        })
        logger.info("Successfully completed and persisted research job %s", job_id)

    except Exception as e:
        logger.exception("Error during execution of research job %s: %s", job_id, str(e))
        job.status = "failed"
        job.error_message = str(e)
        job.current_step = f"Failed: {str(e)}"
        db.commit()
        await broadcast_job_event(job_id, {
            "status": "failed",
            "error_message": str(e),
            "current_step": job.current_step,
        })
    finally:
        db.close()
