# ResearchX — Autonomous Multi-Agent Research & Verification Platform

> A production-grade AI platform that autonomously decomposes complex inquiries, retrieves evidence across heterogeneous sources, cross-validates factual claims, detects conflicting data, and synthesizes citation-grounded intelligence reports using LangGraph, PostgreSQL/pgvector, and React.

---

## 1. The Problem
Standard large language models (LLMs) suffer from severe limitations when deployed for high-stakes enterprise research:
1. **Hallucination & Fabricated Citations**: Models invent plausible-sounding facts and non-existent URLs or papers.
2. **Temporal Blindness & Stale Context**: Inability to synthesize dynamic, real-time market shifts without external tool orchestration.
3. **Silent Compromise on Disagreements**: When multiple credible sources disagree (e.g. diverging funding rounds or revenue numbers), single-prompt LLMs arbitrarily choose one without signaling discrepancy.
4. **Epistemic Conflation**: Facts, reasonable deductions, and pure speculations are presented with identical confidence.

---

## 2. The Solution: ResearchX
ResearchX replaces the standard `User -> LLM -> Answer` pattern with an autonomous **Multi-Agent Research Pipeline**:
- **Query Decomposition**: Deconstructs questions into orthogonal investigation sub-tasks.
- **Parallel Retrieval & Web Ingestion**: Concurrently searches the web, fetches pages safely, and queries internal vector stores.
- **Untrusted Data Sanitization**: Neutralizes prompt injections from external web pages and documents before agent ingestion.
- **Atomic Claim Extraction**: Isolates verifiable assertions and tracks provenance.
- **Cross-Source Fact Verification**: Algorithmically calculates objective confidence scores based on corroboration count and source credibility.
- **Explicit Conflict Detection**: Flags source disagreements with exact divergent figures.
- **Epistemic Classification**: Segregates statements into **FACT**, **INFERENCE**, and **SPECULATION**.
- **Interactive Footnote Citations**: Every claim is linked via `[1]`, `[2]` to verified source snippets.
- **Quality Control Loop**: Rejects and revises drafted reports that fail citation or grounding thresholds.

---

## 3. High-Level Architecture

```
User Inquiry
    │
    ▼
FastAPI Gateway & Job Manager
    │
    ▼
LangGraph Multi-Agent Orchestrator
    ├── 1. Planner Agent (Pydantic Decomposition)
    ├── 2. Parallel Research Agents (Web Search, Safe Fetcher, Anti-Injection)
    ├── 3. Document Intelligence & Hybrid RAG (pgvector + Keyword + Quality)
    ├── 4. Claim Extraction Agent (Atomic Factual Statements)
    ├── 5. Fact Verification Agent (Multi-Source Corroboration & Confidence Scoring)
    ├── 6. Conflict Detection Engine (Discrepancy Highlighting)
    ├── 7. Research Analyst Agent (FACT / INFERENCE / SPECULATION)
    ├── 8. Report Generation Agent (Executive Summary, Markdown Tables, [1] Citations)
    └── 9. Quality Control Agent (Revision Loop if QC Score < Threshold)
    │
    ▼
PostgreSQL / SQLite Persistence + Redis Pub/Sub
    │
    ▼
React Dashboard (Progress Stepper, Report Viewer, Evidence Explorer, React Flow Graph)
```

---

## 4. Specialized Agents

| Agent | Responsibility | Output Type |
|---|---|---|
| **Research Planner Agent** | Analyzes the research question, determines required source categories, and decomposes into orthogonal sub-questions. | Pydantic `ResearchPlan` |
| **Research Agent** | Investigates sub-questions concurrently using search, URL fetcher, and document vector retrieval. | Evidence snippets & source metadata |
| **Claim Extraction Agent** | Isolates atomic factual statements and links them to exact evidence indices. | Extracted factual claims |
| **Fact Verification Agent** | Cross-checks claims against independent sources; computes objective confidence scores ($0.0 - 1.0$). | `VerificationResult` |
| **Conflict Detection Engine** | Explicitly isolates discrepancies between credible sources (e.g. divergent funding figures). | Divergence report cards |
| **Research Analyst Agent** | Synthesizes insights while strictly categorizing statements into `FACT`, `INFERENCE`, or `SPECULATION`. | Structured findings |
| **Report Generation Agent** | Compiles publication-grade Markdown intelligence reports with comparison tables and citation anchors `[1]`, `[2]`. | Markdown report & citation map |
| **Quality Control Agent** | Audits report grounding, validates citation indices, and enforces revision loops if quality score $< 75$. | `QualityAssessmentResult` |

---

## 5. Hybrid Retrieval Pipeline (pgvector + Keyword + Source Quality)

ResearchX combines semantic vector embeddings, BM25 keyword matching, and source reputation scoring:

$$\text{Final Score} = 0.65 \cdot S_{\text{semantic}} + 0.25 \cdot S_{\text{keyword}} + 0.10 \cdot S_{\text{source\_quality}}$$

- **Semantic Score**: Cosine similarity over vector embeddings (`pgvector` or normalized float arrays).
- **Keyword Score**: Token overlap and term density across extracted chunks.
- **Source Quality Score**: System credibility weights (e.g. `.gov`/`.edu`: $0.95$, major financial/tech news: $0.85$, blogs: $0.55$).

---

## 6. Objective Confidence Framework
Findings are mapped to confidence tiers based on evidence agreement, not subjective LLM sentiment:
- **90% - 100% (Very High)**: Corroborated by 3+ independent high-credibility sources with 0 contradictions.
- **75% - 89% (High)**: Corroborated by 2 independent sources with 0 contradictions.
- **50% - 74% (Medium)**: Corroborated by 1 source or minor variance.
- **25% - 49% (Low)**: Low-credibility source or uncorroborated.
- **0% - 24% (Very Low)**: Unverified or contradicted claim.

---

## 7. Evaluation Benchmark Results

The system includes a dedicated 20-sample evaluation dataset (`evaluation/datasets/benchmark_20.json`) and benchmark runner CLI (`python -m evaluation.run_evaluation`):

```text
------------------------- AGGREGATE METRICS -------------------------
Precision At 3               | [###############---------------] |  50.0%
Recall At 5                  | [###################-----------] |  66.7%
Context Relevance            | [#######-----------------------] |  26.6%
Context Completeness         | [####--------------------------] |  16.7%
Faithfulness                 | [##############################] | 100.0%
Claim Support Rate           | [##############################] | 100.0%
Unsupported Claim Rate       | [------------------------------] |   0.0%
Citation Accuracy            | [##############################] | 100.0%
Source Diversity             | [##############################] | 100.0%
Source Quality               | [########################------] |  83.3%
```

---

## 8. Technology Stack

### Backend
- **Python 3.12+** / **FastAPI**
- **LangGraph** (State machine multi-agent orchestration)
- **SQLAlchemy 2.0** / **PostgreSQL** with **pgvector** (SQLite fallback supported)
- **Redis** & **Celery** (Distributed async workers)
- **httpx** & **BeautifulSoup4** (Safe scraping & anti-SSRF URL fetching)
- **pypdf** & **python-docx** (Document intelligence)
- **Pydantic v2** (Strict structured outputs)

### Frontend
- **React 18** / **TypeScript** / **Vite**
- **Tailwind CSS**
- **@xyflow/react** (Interactive React Flow research lineage graph)
- **Recharts** (Telemetry & latency visualizations)
- **Lucide Icons** & **React Markdown**

---

## 9. Quick Start & Setup

### Option 1: Docker Compose (Full Stack)
```bash
# 1. Clone repository
git clone https://github.com/your-username/researchx.git
cd researchx

# 2. Configure environment
cp .env.example .env

# 3. Launch with Docker Compose
docker compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- OpenAPI Swagger: `http://localhost:8000/docs`

---

### Option 2: Standalone Local Setup (Without Docker)

#### 1. Backend Setup
```bash
pip install -r backend/requirements.txt
cd backend
python app/main.py
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 10. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/research` | Create research job & dispatch LangGraph workflow |
| `GET` | `/api/research` | List previous research jobs & statuses |
| `GET` | `/api/research/{job_id}` | Retrieve job metadata and progress percentage |
| `GET` | `/api/research/{job_id}/progress` | Real-time Server-Sent Events (SSE) progress stream |
| `GET` | `/api/research/{job_id}/report` | Retrieve completed report & verified citations |
| `GET` | `/api/research/{job_id}/claims` | Retrieve extracted claims, verification, & evidence |
| `GET` | `/api/research/{job_id}/graph` | React Flow node-link lineage graph data |
| `POST` | `/api/documents/upload` | Upload PDF/DOCX for chunking & vector indexing |
| `POST` | `/api/documents/search` | Execute hybrid search across indexed chunks |
| `GET` | `/api/observability/overview` | Token counts, latency, quality scores, and agent runs |

---

## 11. Testing & Verification

Run the complete test suite:
```bash
python -m pytest backend/tests -v
```
All 10 unit, integration, and E2E tests execute deterministically using the built-in `MockLLMProvider` without requiring external API keys.

Run the evaluation CLI:
```bash
python -m evaluation.run_evaluation --limit 5
```

---

## 12. Resume Positioning
- *"Engineered a full-stack multi-agent AI research platform using LangGraph, RAG, and LLM-based verification to autonomously decompose complex research inquiries, retrieve evidence from heterogeneous sources, cross-validate factual claims, and generate citation-grounded analytical reports."*
- *"Implemented a hybrid retrieval engine using pgvector, BM25 keyword matching, and domain credibility scoring, improving context faithfulness and claim support rates to 100% on benchmark evaluations."*
- *"Designed an agentic verification and conflict detection workflow with recursive quality control loops that identify contradictory sources, calculate objective evidence-based confidence scores, and eliminate unsupported assertions."*
