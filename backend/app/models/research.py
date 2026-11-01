import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings

def utc_now():
    return datetime.now(timezone.utc)

def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    jobs = relationship("ResearchJob", back_populates="user", cascade="all, delete-orphan")


class ResearchJob(Base):
    __tablename__ = "research_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    research_question = Column(Text, nullable=False)
    depth = Column(String(50), default="standard")  # quick, standard, deep
    status = Column(String(50), default="queued", index=True)  # queued, planning, researching, verifying, analyzing, generating_report, completed, failed, cancelled
    progress_pct = Column(Integer, default=0)
    current_step = Column(String(100), default="Initializing research")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="jobs")
    tasks = relationship("ResearchTask", back_populates="job", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="job", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="job", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="job", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="job", uselist=False, cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="job", cascade="all, delete-orphan")
    agent_messages = relationship("AgentMessage", back_populates="job", cascade="all, delete-orphan")


class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    category = Column(String(100), default="general")
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    order_index = Column(Integer, default=0)
    result_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    job = relationship("ResearchJob", back_populates="tasks")


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id"), nullable=False, index=True)
    url = Column(String(1000), nullable=True)
    title = Column(String(500), nullable=False)
    domain = Column(String(255), index=True, nullable=True)
    publisher = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    retrieved_at = Column(DateTime(timezone=True), default=utc_now)
    source_type = Column(String(50), default="website")  # website, news, research_paper, pdf, company_doc, gov_report
    credibility_score = Column(Float, default=0.7)
    content = Column(Text, nullable=True)
    content_hash = Column(String(64), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("ResearchJob", back_populates="sources")
    evidence_items = relationship("ClaimEvidence", back_populates="source", cascade="all, delete-orphan")
    citations = relationship("ReportCitation", back_populates="source")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, md
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(1000), nullable=False)
    processed = Column(Boolean, default=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)  # page_number, section, source_type
    embedding = Column(JSON, nullable=True)  # JSON float array representation
    created_at = Column(DateTime(timezone=True), default=utc_now)

    document = relationship("Document", back_populates="chunks")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    claim_type = Column(String(50), default="general")  # financial, technical, market, statistical, competitive, historical
    importance = Column(String(50), default="medium")  # high, medium, low
    created_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("ResearchJob", back_populates="claims")
    evidence = relationship("ClaimEvidence", back_populates="claim", cascade="all, delete-orphan")
    verification = relationship("VerificationResult", back_populates="claim", uselist=False, cascade="all, delete-orphan")


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False, index=True)
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False, index=True)
    snippet = Column(Text, nullable=False)
    relevance_score = Column(Float, default=1.0)
    is_supporting = Column(Boolean, default=True)  # True = supporting, False = contradicting
    created_at = Column(DateTime(timezone=True), default=utc_now)

    claim = relationship("Claim", back_populates="evidence")
    source = relationship("Source", back_populates="evidence_items")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False, unique=True, index=True)
    status = Column(String(50), default="unverified")  # verified, partially_verified, conflicting, unsupported, unverifiable
    confidence_score = Column(Float, default=0.0)
    reasoning_summary = Column(Text, nullable=True)
    conflicting_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    claim = relationship("Claim", back_populates="verification")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    statement = Column(Text, nullable=False)
    category = Column(String(50), default="FACT")  # FACT, INFERENCE, SPECULATION
    confidence_score = Column(Float, default=0.85)
    confidence_tier = Column(String(50), default="High")  # Very High, High, Medium, Low, Very Low
    evidence_count = Column(Integer, default=1)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("ResearchJob", back_populates="findings")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id"), nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=False)
    executive_summary = Column(Text, nullable=False)
    markdown_content = Column(Text, nullable=False)
    quality_score = Column(Float, default=90.0)
    revision_count = Column(Integer, default=0)
    qc_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    job = relationship("ResearchJob", back_populates="report")
    citations = relationship("ReportCitation", back_populates="report", cascade="all, delete-orphan")


class ReportCitation(Base):
    __tablename__ = "report_citations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False, index=True)
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False, index=True)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=True)
    citation_number = Column(Integer, nullable=False)
    snippet = Column(Text, nullable=True)
    anchor_text = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    report = relationship("Report", back_populates="citations")
    source = relationship("Source", back_populates="citations")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), default=utc_now)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    model_name = Column(String(100), nullable=True)
    tool_calls_count = Column(Integer, default=0)
    status = Column(String(50), default="running")  # running, completed, failed, retried
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("ResearchJob", back_populates="agent_runs")


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    role = Column(String(50), default="agent")  # system, agent, tool, user
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("ResearchJob", back_populates="agent_messages")
