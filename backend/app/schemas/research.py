from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# Planner structured output schema (matches Section 5.1)
class ResearchPlan(BaseModel):
    research_goal: str = Field(description="High level objective of the research")
    sub_questions: List[str] = Field(description="Decomposed atomic sub-questions to investigate")
    research_categories: List[str] = Field(description="e.g. market, companies, technology, competition, financial")
    required_sources: List[str] = Field(description="e.g. news, company websites, research papers, reports")
    priority: str = Field(default="high", description="Priority level: high, medium, low")


# Job creation request
class ResearchJobCreate(BaseModel):
    research_question: str = Field(..., min_length=5, description="The research question to investigate")
    depth: str = Field(default="standard", description="quick, standard, or deep")
    document_ids: Optional[List[str]] = Field(default=None, description="Optional IDs of uploaded documents to search")
    focus_areas: Optional[List[str]] = Field(default=None, description="Optional specific focus categories")


class ResearchJobResponse(BaseModel):
    id: str
    title: str
    research_question: str
    depth: str
    status: str
    progress_pct: int
    current_step: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResearchTaskResponse(BaseModel):
    id: str
    title: str
    category: str
    description: Optional[str] = None
    status: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class SourceResponse(BaseModel):
    id: str
    url: Optional[str] = None
    title: str
    domain: Optional[str] = None
    publisher: Optional[str] = None
    published_at: Optional[datetime] = None
    retrieved_at: datetime
    source_type: str
    credibility_score: float
    content_snippet: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClaimEvidenceResponse(BaseModel):
    id: str
    source_id: str
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    snippet: str
    relevance_score: float
    is_supporting: bool

    model_config = ConfigDict(from_attributes=True)


class VerificationResultResponse(BaseModel):
    status: str
    confidence_score: float
    reasoning_summary: Optional[str] = None
    conflicting_notes: Optional[str] = None


class ClaimResponse(BaseModel):
    id: str
    claim_text: str
    claim_type: str
    importance: str
    verification: Optional[VerificationResultResponse] = None
    evidence: List[ClaimEvidenceResponse] = []

    model_config = ConfigDict(from_attributes=True)


class FindingResponse(BaseModel):
    id: str
    title: str
    statement: str
    category: str  # FACT, INFERENCE, SPECULATION
    confidence_score: float
    confidence_tier: str  # Very High, High, Medium, Low, Very Low
    evidence_count: int
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class ReportCitationResponse(BaseModel):
    citation_number: int
    source_id: str
    source_title: str
    source_url: Optional[str] = None
    source_domain: Optional[str] = None
    snippet: Optional[str] = None


class ReportResponse(BaseModel):
    id: str
    job_id: str
    title: str
    executive_summary: str
    markdown_content: str
    quality_score: float
    revision_count: int
    qc_notes: Optional[str] = None
    citations: List[ReportCitationResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Graph visualization response (compatible with React Flow)
class GraphNode(BaseModel):
    id: str
    type: str  # question, task, source, claim, verification, finding
    data: Dict[str, Any]
    position: Dict[str, float]


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    animated: Optional[bool] = False


class ResearchGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# Observability schemas
class AgentRunResponse(BaseModel):
    id: str
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: int
    input_tokens: int
    output_tokens: int
    model_name: Optional[str] = None
    tool_calls_count: int
    status: str
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ObservabilityOverview(BaseModel):
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    avg_duration_seconds: float
    total_tokens_used: int
    estimated_cost_usd: float
    avg_confidence_score: float
    avg_quality_score: float
    agent_runs: List[AgentRunResponse] = []


# Document schemas
class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    metadata_json: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    processed: bool
    summary: Optional[str] = None
    chunks_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
