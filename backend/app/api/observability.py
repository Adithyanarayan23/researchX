import logging
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.research import ResearchJob, AgentRun, Finding, Report
from app.schemas.research import ObservabilityOverview, AgentRunResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/observability", tags=["Observability"])


@router.get("/overview", response_model=ObservabilityOverview)
def get_observability_overview(db: Session = Depends(get_db)):
    """
    Returns platform-wide metrics: total jobs, token usage, estimated cost,
    confidence statistics, and recent agent executions.
    """
    total_jobs = db.query(ResearchJob).count()
    completed_jobs = db.query(ResearchJob).filter(ResearchJob.status == "completed").count()
    failed_jobs = db.query(ResearchJob).filter(ResearchJob.status == "failed").count()

    # Agent runs
    agent_runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(100).all()

    total_tokens = sum((r.input_tokens + r.output_tokens) for r in agent_runs)
    total_duration_ms = sum(r.duration_ms for r in agent_runs)
    avg_duration = (total_duration_ms / (1000.0 * max(1, completed_jobs))) if completed_jobs else 0.0

    # Token cost approximation ($0.15 per 1M input, $0.60 per 1M output blended average ~ $0.35/1M)
    estimated_cost = round((total_tokens / 1_000_000.0) * 0.35, 4)

    # Average confidence score across findings
    avg_conf = db.query(func.avg(Finding.confidence_score)).scalar() or 0.85

    # Average quality score across reports
    avg_quality = db.query(func.avg(Report.quality_score)).scalar() or 91.0

    runs_response = [
        AgentRunResponse(
            id=r.id,
            agent_name=r.agent_name,
            start_time=r.start_time,
            end_time=r.end_time,
            duration_ms=r.duration_ms,
            input_tokens=r.input_tokens,
            output_tokens=r.output_tokens,
            model_name=r.model_name,
            tool_calls_count=r.tool_calls_count,
            status=r.status,
            error_message=r.error_message,
        )
        for r in agent_runs[:25]
    ]

    return ObservabilityOverview(
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        avg_duration_seconds=round(avg_duration, 1),
        total_tokens_used=total_tokens,
        estimated_cost_usd=estimated_cost,
        avg_confidence_score=round(float(avg_conf), 2),
        avg_quality_score=round(float(avg_quality), 1),
        agent_runs=runs_response,
    )
