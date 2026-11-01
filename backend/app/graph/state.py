from typing import TypedDict, List, Dict, Any, Optional


class ResearchGraphState(TypedDict):
    job_id: str
    research_question: str
    depth: str
    document_ids: Optional[List[str]]
    plan: Optional[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    claims: List[Dict[str, Any]]
    verified_claims: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    report: Optional[Dict[str, Any]]
    quality_assessment: Optional[Dict[str, Any]]
    revision_count: int
    current_step: str
    progress_pct: int
    agent_runs: List[Dict[str, Any]]
    error: Optional[str]
