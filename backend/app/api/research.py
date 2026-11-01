import asyncio
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.research import (
    ResearchJob,
    ResearchTask,
    Source,
    Claim,
    Finding,
    Report,
    ReportCitation,
)
from app.schemas.research import (
    ResearchJobCreate,
    ResearchJobResponse,
    ResearchTaskResponse,
    SourceResponse,
    ClaimResponse,
    FindingResponse,
    ReportResponse,
    ReportCitationResponse,
    ResearchGraphResponse,
    GraphNode,
    GraphEdge,
)
from app.services.job_manager import (
    execute_research_workflow,
    register_job_listener,
    unregister_job_listener,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["Research"])


@router.post("", response_model=ResearchJobResponse)
async def create_research_job(
    payload: ResearchJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Creates a new research job and asynchronously launches the multi-agent LangGraph workflow.
    """
    # Create DB record
    job = ResearchJob(
        title=payload.research_question[:100],
        research_question=payload.research_question,
        depth=payload.depth,
        status="queued",
        progress_pct=0,
        current_step="Queued for multi-agent investigation",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Launch execution asynchronously
    background_tasks.add_task(execute_research_workflow, job.id)

    return job


@router.get("", response_model=List[ResearchJobResponse])
def list_research_jobs(limit: int = 50, db: Session = Depends(get_db)):
    """List previous research jobs."""
    jobs = db.query(ResearchJob).order_by(ResearchJob.created_at.desc()).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=ResearchJobResponse)
def get_research_job(job_id: str, db: Session = Depends(get_db)):
    """Get research job status and metadata."""
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    return job


@router.get("/{job_id}/progress")
async def stream_job_progress(job_id: str, db: Session = Depends(get_db)):
    """
    Server-Sent Events (SSE) streaming endpoint for real-time progress updates.
    """
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")

    async def event_generator():
        queue = register_job_listener(job_id)
        # Send initial status
        initial_payload = {
            "status": job.status,
            "progress_pct": job.progress_pct,
            "current_step": job.current_step,
        }
        yield f"data: {json.dumps(initial_payload)}\n\n"

        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=25.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    if event.get("status") in ("completed", "failed", "cancelled"):
                        break
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat
                    yield f": ping\n\n"
        finally:
            unregister_job_listener(job_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/{job_id}/tasks", response_model=List[ResearchTaskResponse])
def get_job_tasks(job_id: str, db: Session = Depends(get_db)):
    tasks = db.query(ResearchTask).filter(ResearchTask.job_id == job_id).order_by(ResearchTask.order_index).all()
    return tasks


@router.get("/{job_id}/sources", response_model=List[SourceResponse])
def get_job_sources(job_id: str, db: Session = Depends(get_db)):
    sources = db.query(Source).filter(Source.job_id == job_id).all()
    return [
        SourceResponse(
            id=s.id,
            url=s.url,
            title=s.title,
            domain=s.domain,
            publisher=s.publisher,
            published_at=s.published_at,
            retrieved_at=s.retrieved_at,
            source_type=s.source_type,
            credibility_score=s.credibility_score,
            content_snippet=(s.content[:250] + "...") if s.content else None,
        )
        for s in sources
    ]


@router.get("/{job_id}/claims", response_model=List[ClaimResponse])
def get_job_claims(job_id: str, db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(Claim.job_id == job_id).all()
    result = []
    for c in claims:
        verif_data = None
        if c.verification:
            verif_data = {
                "status": c.verification.status,
                "confidence_score": c.verification.confidence_score,
                "reasoning_summary": c.verification.reasoning_summary,
                "conflicting_notes": c.verification.conflicting_notes,
            }

        ev_list = []
        for ev in c.evidence:
            ev_list.append({
                "id": ev.id,
                "source_id": ev.source_id,
                "source_title": ev.source.title if ev.source else "Source",
                "source_url": ev.source.url if ev.source else None,
                "snippet": ev.snippet,
                "relevance_score": ev.relevance_score,
                "is_supporting": ev.is_supporting,
            })

        result.append(
            ClaimResponse(
                id=c.id,
                claim_text=c.claim_text,
                claim_type=c.claim_type,
                importance=c.importance,
                verification=verif_data,
                evidence=ev_list,
            )
        )
    return result


@router.get("/{job_id}/findings", response_model=List[FindingResponse])
def get_job_findings(job_id: str, db: Session = Depends(get_db)):
    findings = db.query(Finding).filter(Finding.job_id == job_id).order_by(Finding.order_index).all()
    return findings


@router.get("/{job_id}/report", response_model=ReportResponse)
def get_job_report(job_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.job_id == job_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")

    citations_resp = []
    for cit in report.citations:
        citations_resp.append(
            ReportCitationResponse(
                citation_number=cit.citation_number,
                source_id=cit.source_id,
                source_title=cit.source.title if cit.source else "Source",
                source_url=cit.source.url if cit.source else None,
                source_domain=cit.source.domain if cit.source else None,
                snippet=cit.snippet,
            )
        )

    return ReportResponse(
        id=report.id,
        job_id=report.job_id,
        title=report.title,
        executive_summary=report.executive_summary,
        markdown_content=report.markdown_content,
        quality_score=report.quality_score,
        revision_count=report.revision_count,
        qc_notes=report.qc_notes,
        citations=citations_resp,
        created_at=report.created_at,
    )


@router.get("/{job_id}/graph", response_model=ResearchGraphResponse)
def get_research_graph(job_id: str, db: Session = Depends(get_db)):
    """
    Constructs an interactive React Flow node-link graph of the entire research lineage:
    Question -> Sub-Tasks -> Sources -> Claims -> Verification -> Findings.
    """
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    tasks = db.query(ResearchTask).filter(ResearchTask.job_id == job_id).all()
    sources = db.query(Source).filter(Source.job_id == job_id).all()
    claims = db.query(Claim).filter(Claim.job_id == job_id).all()
    findings = db.query(Finding).filter(Finding.job_id == job_id).all()

    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []

    # 1. Root Question Node
    q_id = "node_question"
    nodes.append(
        GraphNode(
            id=q_id,
            type="question",
            data={"label": job.research_question, "depth": job.depth, "title": "Research Question"},
            position={"x": 500.0, "y": 50.0},
        )
    )

    # 2. Task Nodes
    task_y = 200.0
    task_spacing = max(200.0, 1000.0 / max(1, len(tasks)))
    for idx, t in enumerate(tasks):
        t_id = f"task_{t.id}"
        x = 100.0 + idx * task_spacing
        nodes.append(
            GraphNode(
                id=t_id,
                type="task",
                data={"label": t.title, "category": t.category, "status": t.status},
                position={"x": x, "y": task_y},
            )
        )
        edges.append(
            GraphEdge(
                id=f"e_{q_id}_{t_id}",
                source=q_id,
                target=t_id,
                animated=True,
            )
        )

    # 3. Source Nodes
    source_y = 380.0
    source_spacing = max(180.0, 1000.0 / max(1, len(sources)))
    for idx, s in enumerate(sources[:8]):  # show top 8 for clean visualization
        s_id = f"src_{s.id}"
        x = 80.0 + idx * source_spacing
        nodes.append(
            GraphNode(
                id=s_id,
                type="source",
                data={
                    "label": s.title[:40] + ("..." if len(s.title) > 40 else ""),
                    "domain": s.domain,
                    "credibility": s.credibility_score,
                },
                position={"x": x, "y": source_y},
            )
        )
        # Connect to closest task
        if tasks:
            closest_task = tasks[idx % len(tasks)]
            edges.append(
                GraphEdge(
                    id=f"e_task_{closest_task.id}_{s_id}",
                    source=f"task_{closest_task.id}",
                    target=s_id,
                )
            )

    # 4. Claim Nodes
    claim_y = 560.0
    claim_spacing = max(220.0, 1000.0 / max(1, len(claims)))
    for idx, c in enumerate(claims[:6]):
        c_id = f"claim_{c.id}"
        x = 100.0 + idx * claim_spacing
        v_status = c.verification.status if c.verification else "unverified"
        conf = c.verification.confidence_score if c.verification else 0.5
        nodes.append(
            GraphNode(
                id=c_id,
                type="claim",
                data={
                    "label": c.claim_text[:50] + "...",
                    "type": c.claim_type,
                    "status": v_status,
                    "confidence": conf,
                },
                position={"x": x, "y": claim_y},
            )
        )
        # Connect to sources
        if sources:
            src_conn = sources[idx % len(sources)]
            edges.append(
                GraphEdge(
                    id=f"e_src_{src_conn.id}_{c_id}",
                    source=f"src_{src_conn.id}",
                    target=c_id,
                )
            )

    # 5. Finding Nodes
    find_y = 740.0
    find_spacing = max(240.0, 1000.0 / max(1, len(findings)))
    for idx, f in enumerate(findings[:5]):
        f_id = f"find_{f.id}"
        x = 120.0 + idx * find_spacing
        nodes.append(
            GraphNode(
                id=f_id,
                type="finding",
                data={
                    "label": f.title,
                    "category": f.category,
                    "confidence": f.confidence_tier,
                },
                position={"x": x, "y": find_y},
            )
        )
        # Connect from claims
        if claims:
            clm_conn = claims[idx % len(claims)]
            edges.append(
                GraphEdge(
                    id=f"e_clm_{clm_conn.id}_{f_id}",
                    source=f"claim_{clm_conn.id}",
                    target=f_id,
                    animated=True,
                )
            )

    return ResearchGraphResponse(nodes=nodes, edges=edges)


@router.post("/{job_id}/cancel")
def cancel_research_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = "cancelled"
    job.current_step = "Job cancelled by user"
    db.commit()
    return {"message": "Job cancelled successfully"}
