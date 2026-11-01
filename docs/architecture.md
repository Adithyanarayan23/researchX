# ResearchX — Technical Architecture & Design Documentation

## 1. System Mission
ResearchX addresses the structural vulnerabilities of single-prompt LLM generation (hallucination, lack of verifiable grounding, temporal blindness, and inability to handle conflicting facts) by implementing an autonomous, multi-agent decomposition, verification, and synthesis pipeline.

---

## 2. Multi-Agent Topology (LangGraph)

```text
[User Inquiry]
      │
      ▼
┌──────────────┐
│ PlannerAgent │  Decomposes inquiry into atomic sub-questions & categories
└──────┬───────┘
      │
      ▼
┌──────────────────┐
│ Task Generator   │  Dispatches parallel investigation units
└──────┬───────────┘
      │
      ▼
┌──────────────────────┐
│ Parallel Researchers │  Web Search + Safe URL Fetcher + pgvector Document RAG
└──────┬───────────────┘
      │
      ▼
┌────────────────────┐
│ Evidence Collector │  Deduplication via SHA-256 + Credibility Scoring
└──────┬─────────────┘
      │
      ▼
┌──────────────────────┐
│ ClaimExtractionAgent │  Isolates atomic factual statements & attaches evidence IDs
└──────┬───────────────┘
      │
      ▼
┌─────────────────────────┐
│ FactVerificationAgent   │  Multi-source corroboration & objective confidence scoring
└──────┬──────────────────┘
      │
      ▼
┌──────────────────────┐
│ Conflict Detection   │  Explicitly details divergence (e.g. $25M vs $22M)
└──────┬───────────────┘
      │
      ▼
┌──────────────────────┐
│ ResearchAnalystAgent │  Categorizes findings: FACT vs INFERENCE vs SPECULATION
└──────┬───────────────┘
      │
      ▼
┌────────────────────────┐
│ ReportGenerationAgent  │  Compiles Executive Summary, Tables, & [1], [2] Citations
└──────┬─────────────────┘
      │
      ▼
┌──────────────────────┐
│ QualityControlAgent  │◄─── (Revision Loop if Quality Score < Threshold)
└──────┬───────────────┘
      │ (Quality Score >= Threshold)
      ▼
[Final Publication & Persistence]
```

---

## 3. Epistemic Classification Framework
Every analytical claim is strictly graded into three transparent tiers:
- **FACT**: Directly corroborated by two or more independent, verified sources.
- **INFERENCE**: Deductive or inductive logical conclusion drawn from multiple verified facts.
- **SPECULATION**: Forward-looking hypothesis or scenario lacking complete confirmation.

---

## 4. Objective Confidence Scoring Methodology
Rather than relying on the LLM's subjective sentiment, confidence is computed algorithmically:

$$\text{Confidence} = f(N_{\text{supporting}}, N_{\text{contradicting}}, \bar{C}_{\text{sources}}, \text{Status})$$

- $\mathbf{90\% - 100\%}$ (**Very High**): Corroborated by 3+ independent high-credibility sources with 0 contradictions.
- $\mathbf{75\% - 89\%}$ (**High**): Corroborated by 2 independent sources with 0 contradictions.
- $\mathbf{50\% - 74\%}$ (**Medium**): Single credible source or minor discrepancies.
- $\mathbf{25\% - 49\%}$ (**Low**): Insufficient corroboration or low domain credibility.
- $\mathbf{0\% - 24\%}$ (**Very Low**): Unverified or explicitly refuted claim.

---

## 5. Security & Prompt Injection Mitigation
- Untrusted web content passes through `sanitize_untrusted_content` which neutralizes prompt injection signatures (e.g. `ignore previous instructions`, `reveal system prompt`).
- SSRF protection in `is_safe_url` prevents internal network probing, link-local endpoints, and cloud metadata services (`169.254.169.254`).
