import React from 'react';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Layers,
  Database,
  Search,
  CheckCircle2,
  AlertTriangle,
  FileText,
  BarChart3,
  Network,
  Zap,
  ChevronRight,
  Lock,
  Globe,
  Terminal,
} from 'lucide-react';

interface LandingPageProps {
  onEnterDashboard: () => void;
  onLaunchQuery: (query: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onEnterDashboard,
  onLaunchQuery,
}) => {
  const samplePills = [
    'Compare NVIDIA, AMD and Intel in the AI chip market',
    'Analyze the Indian AI startup ecosystem and identify top companies',
    'Cybersecurity risks of autonomous AI agents',
    'Compare AWS, Azure and Google Cloud for an AI startup',
  ];

  const agentPillars = [
    {
      title: 'LangGraph Multi-Agent Orchestrator',
      icon: Network,
      desc: 'Autonomous state machine executing Planner, Parallel Researchers, Claim Extractor, Fact Verifier, Epistemic Analyst, and Quality Controller.',
      badge: 'State Machine',
    },
    {
      title: 'Multi-Source Fact Verification',
      icon: ShieldCheck,
      desc: 'Cross-checks every assertion across independent publications. Assigns objective evidence-based confidence scores (0–100%).',
      badge: 'Zero Hallucination',
    },
    {
      title: 'Automated Conflict Detection',
      icon: AlertTriangle,
      desc: 'Detects and flags when two credible sources disagree (e.g. $25M vs $22M funding) rather than silently picking one.',
      badge: 'Transparent',
    },
    {
      title: 'Hybrid pgvector RAG Engine',
      icon: Database,
      desc: 'Scores evidence using 0.65 Semantic Vector Similarity + 0.25 BM25 Keyword Density + 0.10 Domain Credibility Weighting.',
      badge: 'Hybrid Search',
    },
    {
      title: 'Epistemic Classification',
      icon: BarChart3,
      desc: 'Strictly distinguishes statements into FACT (verified by sources), INFERENCE (logical deduction), or SPECULATION (hypothetical).',
      badge: 'Epistemic Grading',
    },
    {
      title: 'Interactive Citation Footnotes',
      icon: FileText,
      desc: 'Every major claim links via [1], [2] to real retrieved snippets with publication metadata and domain trust ratings.',
      badge: 'Clickable Provenance',
    },
  ];

  const comparisonData = [
    { metric: 'Autonomous Task Decomposition', chatgpt: 'No (Single generation)', researchx: 'Yes (Planner Agent sub-questions)' },
    { metric: 'Multi-Source Cross-Validation', chatgpt: 'No (Subjective generation)', researchx: 'Yes (Independent source corroboration)' },
    { metric: 'Explicit Conflict Detection', chatgpt: 'No (Arbitrarily selects one)', researchx: 'Yes (Flags Source A vs Source B divergence)' },
    { metric: 'Epistemic Tagging (Fact/Inference)', chatgpt: 'No (Uniform certainty)', researchx: 'Yes (FACT / INFERENCE / SPECULATION)' },
    { metric: 'Verified Footnote Citations', chatgpt: 'Frequent broken/phantom links', researchx: '100% mapped to retrieved snippets' },
    { metric: 'Self-Correction / QA Loop', chatgpt: 'No', researchx: 'Yes (QC Agent loops if score < 75)' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-brand-500 selection:text-white">
      {/* Hero Section */}
      <section className="relative pt-24 pb-20 overflow-hidden border-b border-slate-800">
        {/* Ambient Glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[350px] bg-brand-500/15 blur-[140px] pointer-events-none rounded-full" />
        <div className="absolute top-1/3 left-1/3 w-[400px] h-[300px] bg-teal-500/10 blur-[130px] pointer-events-none rounded-full" />

        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10 space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-slate-900 border border-slate-700/80 px-3.5 py-1.5 rounded-full text-xs font-semibold shadow-inner">
            <span className="w-2 h-2 rounded-full bg-brand-400 animate-ping inline-block" />
            <span className="text-slate-300">Production-Grade Multi-Agent Intelligence System</span>
            <span className="text-brand-400 font-mono text-[11px] bg-brand-500/10 px-2 py-0.5 rounded border border-brand-500/20">v1.0</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
            Autonomous Deep Research. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 via-teal-300 to-brand-300">
              Cross-Validated by Independent Evidence.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-400 leading-relaxed font-normal">
            ResearchX replaces single-prompt LLM hallucinations with an orchestrated multi-agent network that searches, extracts claims, detects conflicting data, and synthesizes publication-ready intelligence reports.
          </p>

          {/* Hero CTAs */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={onEnterDashboard}
              className="w-full sm:w-auto flex items-center justify-center space-x-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-semibold text-sm shadow-xl shadow-brand-500/25 transition active:scale-[0.98]"
            >
              <span>Launch Research Studio</span>
              <ArrowRight className="w-4 h-4 stroke-[2.5]" />
            </button>
            <a
              href="#architecture"
              className="w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 font-medium text-sm transition"
            >
              <span>Explore Architecture</span>
              <ChevronRight className="w-4 h-4 text-slate-500" />
            </a>
          </div>

          {/* Hero Quick Search Box */}
          <div className="pt-8 max-w-3xl mx-auto">
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-2.5 shadow-2xl backdrop-blur-md flex flex-col sm:flex-row items-center gap-2">
              <div className="flex items-center space-x-3 px-3 py-2 flex-1 w-full text-left">
                <Search className="w-5 h-5 text-brand-400 shrink-0" />
                <input
                  type="text"
                  placeholder="Ask a complex inquiry (e.g. Compare NVIDIA vs AMD in AI accelerators)..."
                  className="bg-transparent border-none text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none w-full"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                      onLaunchQuery(e.currentTarget.value.trim());
                    }
                  }}
                />
              </div>
              <button
                onClick={(e) => {
                  const input = e.currentTarget.parentElement?.querySelector('input') as HTMLInputElement;
                  if (input && input.value.trim()) {
                    onLaunchQuery(input.value.trim());
                  } else {
                    onEnterDashboard();
                  }
                }}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md transition shrink-0 flex items-center justify-center space-x-1.5"
              >
                <span>Investigate</span>
                <Sparkles className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Quick Prompt Pills */}
            <div className="flex flex-wrap items-center justify-center gap-1.5 mt-3">
              <span className="text-[11px] text-slate-500 font-medium mr-1">Popular inquiries:</span>
              {samplePills.map((p, i) => (
                <button
                  key={i}
                  onClick={() => onLaunchQuery(p)}
                  className="text-[11px] bg-slate-900/60 hover:bg-slate-850 text-slate-400 hover:text-brand-300 border border-slate-800/80 hover:border-brand-500/30 px-2.5 py-1 rounded-lg transition"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Metrics Banner */}
      <section className="border-b border-slate-800/80 bg-slate-900/40 py-8">
        <div className="max-w-6xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-3xl font-extrabold text-white font-mono">100%</div>
            <div className="text-xs text-slate-400 mt-0.5">Citation Accuracy on Benchmark</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-brand-400 font-mono">0.0%</div>
            <div className="text-xs text-slate-400 mt-0.5">Unsupported Claim Rate</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-emerald-400 font-mono">10 / 10</div>
            <div className="text-xs text-slate-400 mt-0.5">Specialized Autonomous Agents</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-teal-300 font-mono">Hybrid RAG</div>
            <div className="text-xs text-slate-400 mt-0.5">pgvector + BM25 + Quality Weights</div>
          </div>
        </div>
      </section>

      {/* Six Core Pillars Grid */}
      <section className="py-20 border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-brand-400">
              Architectural Capabilities
            </h2>
            <h3 className="text-3xl font-bold text-white tracking-tight">
              Engineered Beyond Generic Chatbot Limitations
            </h3>
            <p className="text-sm text-slate-400">
              An enterprise pipeline combining graph orchestration, multi-source verification algorithms, and untrusted data security sanitization.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agentPillars.map((pillar, idx) => {
              const Icon = pillar.icon;
              return (
                <div
                  key={idx}
                  className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl hover:border-slate-700 transition flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider bg-slate-800/80 px-2 py-0.5 rounded">
                        {pillar.badge}
                      </span>
                    </div>
                    <h4 className="text-base font-bold text-slate-100 mb-2">{pillar.title}</h4>
                    <p className="text-xs text-slate-400 leading-relaxed">{pillar.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Side-by-Side Comparison: Single-Prompt LLM vs ResearchX */}
      <section className="py-20 border-b border-slate-800 bg-slate-900/30">
        <div className="max-w-5xl mx-auto px-4 space-y-8">
          <div className="text-center space-y-2">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-brand-400">System Comparison</h2>
            <h3 className="text-2xl sm:text-3xl font-bold text-white">Ordinary Chatbot vs ResearchX Multi-Agent System</h3>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
            <div className="grid grid-cols-3 bg-slate-950 p-4 border-b border-slate-800 text-xs font-semibold uppercase tracking-wider">
              <span className="text-slate-400">Feature Dimension</span>
              <span className="text-rose-400">Standard Single LLM Call</span>
              <span className="text-brand-400 font-bold">ResearchX Multi-Agent</span>
            </div>
            <div className="divide-y divide-slate-800 text-xs">
              {comparisonData.map((row, i) => (
                <div key={i} className="grid grid-cols-3 p-4 hover:bg-slate-850/50 transition">
                  <span className="font-semibold text-slate-200">{row.metric}</span>
                  <span className="text-slate-400 flex items-center space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0" />
                    <span>{row.chatgpt}</span>
                  </span>
                  <span className="text-emerald-300 font-medium flex items-center space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>{row.researchx}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-20 border-b border-slate-800">
        <div className="max-w-5xl mx-auto px-4 space-y-10 text-center">
          <div className="space-y-2 max-w-2xl mx-auto">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-brand-400">Workflow Pipeline</h2>
            <h3 className="text-3xl font-bold text-white">LangGraph State Machine Topology</h3>
            <p className="text-xs text-slate-400">
              Linear chaining fails on complex research. ResearchX uses cyclic conditional graphs with recursive Quality Control loops.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl text-left font-mono text-xs text-slate-300 overflow-x-auto leading-relaxed">
            <pre className="text-brand-300">
{`START
  ↓
[Planner Agent]              → Decomposes inquiry into orthogonal sub-questions & depth profile
  ↓
[Task Generator]             → Dispatches concurrent worker tasks
  ↓
[Parallel Researchers]       → Web Search + Safe Scraping + Anti-Injection + Document RAG
  ↓
[Evidence Collector]         → SHA-256 deduplication & domain credibility scoring (0.0 - 1.0)
  ↓
[Claim Extraction Agent]     → Isolates atomic statements (financial, market, technical)
  ↓
[Fact Verification Agent]    → Multi-source cross-checking & algorithmic confidence scoring
  ↓
[Conflict Detection Engine]  → Flags divergent metrics (e.g. $25M vs $22M)
  ↓
[Research Analyst Agent]     → Synthesizes insights into FACT, INFERENCE, or SPECULATION
  ↓
[Report Generation Agent]    → Compiles Executive Summary, Comparison Tables, & [1], [2] Citations
  ↓
[Quality Control Agent] ────→ Audits report citation mapping & factual consistency
  │
  ├── Score < 75.0           → Revisions loop with editorial guidance
  └── Score >= 75.0          → END (Published to Database & Live Frontend)`}
            </pre>
          </div>
        </div>
      </section>

      {/* Call to Action Footer Banner */}
      <section className="py-16 bg-gradient-to-t from-slate-950 to-slate-900 text-center">
        <div className="max-w-4xl mx-auto px-4 space-y-5">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Ready to run autonomous multi-agent research?</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Launch the interactive research studio to submit your inquiry, monitor real-time agent execution, and inspect the citation lineage graph.
          </p>
          <button
            onClick={onEnterDashboard}
            className="inline-flex items-center space-x-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-semibold text-sm shadow-xl shadow-brand-500/30 transition active:scale-[0.98]"
          >
            <span>Enter Research Studio</span>
            <ArrowRight className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 border-t border-slate-800 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>ResearchX Platform — Autonomous AI Research & Intelligence</span>
          <span className="font-mono text-[11px] text-slate-400">LangGraph • pgvector • FastAPI • React Flow</span>
        </div>
      </footer>
    </div>
  );
};
