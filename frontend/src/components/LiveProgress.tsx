import React, { useEffect, useState, useRef } from 'react';
import {
  Activity,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileSearch,
  Database,
  ShieldCheck,
  BarChart3,
  FileCheck2,
  Cpu,
  ArrowRight,
  Terminal,
} from 'lucide-react';
import { ResearchJob } from '../types';

interface LiveProgressProps {
  job: ResearchJob | null;
  onViewReport: (jobId: string) => void;
}

interface StepLog {
  timestamp: string;
  message: string;
  node?: string;
}

export const LiveProgress: React.FC<LiveProgressProps> = ({ job, onViewReport }) => {
  const [progressPct, setProgressPct] = useState(job?.progress_pct || 0);
  const [currentStep, setCurrentStep] = useState(job?.current_step || 'Initializing investigation');
  const [status, setStatus] = useState(job?.status || 'queued');
  const [sourcesCount, setSourcesCount] = useState(0);
  const [claimsCount, setClaimsCount] = useState(0);
  const [conflictsCount, setConflictsCount] = useState(0);
  const [logs, setLogs] = useState<StepLog[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!job) return;

    setProgressPct(job.progress_pct);
    setCurrentStep(job.current_step);
    setStatus(job.status);

    // Establish Server-Sent Events (SSE) connection
    const eventSource = new EventSource(`/api/research/${job.id}/progress`);

    eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.progress_pct !== undefined) setProgressPct(data.progress_pct);
        if (data.current_step) {
          setCurrentStep(data.current_step);
          setLogs((prev) => [
            ...prev,
            {
              timestamp: new Date().toLocaleTimeString(),
              message: data.current_step,
              node: data.node,
            },
          ]);
        }
        if (data.status) setStatus(data.status);
        if (data.sources_count) setSourcesCount(data.sources_count);
        if (data.claims_count) setClaimsCount(data.claims_count);
        if (data.conflicts_count !== undefined) setConflictsCount(data.conflicts_count);

        if (data.status === 'completed' || data.status === 'failed') {
          eventSource.close();
        }
      } catch (err) {
        // Heartbeat or malformed event
      }
    };

    eventSource.onerror = () => {
      // Stream completed or error
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [job?.id]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  if (!job) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center text-slate-400">
        <Activity className="w-12 h-12 mx-auto text-slate-600 mb-3" />
        <p className="text-base font-medium">No research job currently active.</p>
        <p className="text-xs text-slate-500 mt-1">Start a new inquiry from the top bar or select one from the dashboard.</p>
      </div>
    );
  }

  const steps = [
    { id: 'planning', label: 'Planner Agent', desc: 'Query decomposition', icon: FileSearch },
    { id: 'researching', label: 'Parallel Research', desc: 'Multi-source retrieval', icon: Database },
    { id: 'verifying', label: 'Fact Verification', desc: 'Cross-checking & conflict check', icon: ShieldCheck },
    { id: 'analyzing', label: 'Research Analyst', desc: 'FACT vs INFERENCE', icon: BarChart3 },
    { id: 'generating_report', label: 'Report Generation', desc: 'Grounding citations', icon: FileCheck2 },
    { id: 'completed', label: 'Quality Control', desc: 'Audited & Published', icon: Cpu },
  ];

  const getStepState = (stepId: string) => {
    const order = ['queued', 'planning', 'researching', 'verifying', 'analyzing', 'generating_report', 'completed'];
    const currentIdx = order.indexOf(status);
    const stepIdx = order.indexOf(stepId);

    if (status === 'completed') return 'completed';
    if (status === 'failed') return 'failed';
    if (currentIdx > stepIdx) return 'completed';
    if (currentIdx === stepIdx) return 'active';
    return 'pending';
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      {/* Overview Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center space-x-2 mb-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-brand-400 bg-brand-500/10 px-2.5 py-0.5 rounded-full border border-brand-500/20">
                Job ID: {job.id.slice(0, 8)}
              </span>
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">
                Depth: {job.depth}
              </span>
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight leading-snug">
              {job.research_question}
            </h1>
          </div>

          {status === 'completed' && (
            <button
              onClick={() => onViewReport(job.id)}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30 transition shrink-0 active:scale-[0.98]"
            >
              <span>View Intelligence Report</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-300 flex items-center space-x-2">
              {status !== 'completed' && status !== 'failed' && (
                <span className="w-2 h-2 rounded-full bg-brand-400 animate-ping inline-block" />
              )}
              <span>{currentStep}</span>
            </span>
            <span className="text-brand-400 font-mono">{progressPct}%</span>
          </div>
          <div className="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden border border-slate-800/80">
            <div
              className={`h-full transition-all duration-500 ease-out rounded-full ${
                status === 'completed'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                  : status === 'failed'
                  ? 'bg-rose-500'
                  : 'bg-gradient-to-r from-brand-600 to-brand-400'
              }`}
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>

        {/* Live Counters */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-slate-800">
          <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
            <div className="text-[11px] text-slate-400 font-medium">Status</div>
            <div className="text-base font-bold text-white uppercase tracking-tight mt-0.5">
              {status.replace('_', ' ')}
            </div>
          </div>
          <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
            <div className="text-[11px] text-slate-400 font-medium">Vetted Sources</div>
            <div className="text-base font-bold text-emerald-400 font-mono mt-0.5">{sourcesCount}</div>
          </div>
          <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
            <div className="text-[11px] text-slate-400 font-medium">Extracted Claims</div>
            <div className="text-base font-bold text-brand-400 font-mono mt-0.5">{claimsCount}</div>
          </div>
          <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
            <div className="text-[11px] text-slate-400 font-medium">Flagged Conflicts</div>
            <div className="text-base font-bold text-amber-400 font-mono mt-0.5">{conflictsCount}</div>
          </div>
        </div>
      </div>

      {/* Stepper Pipeline */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
          Autonomous Agent Execution Pipeline
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          {steps.map((st, i) => {
            const Icon = st.icon;
            const state = getStepState(st.id);
            return (
              <div
                key={st.id}
                className={`p-3.5 rounded-xl border transition-all text-left relative overflow-hidden ${
                  state === 'completed'
                    ? 'border-emerald-500/30 bg-emerald-500/5'
                    : state === 'active'
                    ? 'border-brand-500 bg-brand-500/10 ring-2 ring-brand-500/20'
                    : 'border-slate-800/60 bg-slate-950/40 opacity-60'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <Icon
                    className={`w-5 h-5 ${
                      state === 'completed'
                        ? 'text-emerald-400'
                        : state === 'active'
                        ? 'text-brand-400 animate-pulse'
                        : 'text-slate-500'
                    }`}
                  />
                  {state === 'completed' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : state === 'active' ? (
                    <Clock className="w-4 h-4 text-brand-400 animate-spin" />
                  ) : (
                    <span className="text-[10px] text-slate-500 font-mono">0{i + 1}</span>
                  )}
                </div>
                <div className="text-xs font-bold text-slate-200">{st.label}</div>
                <div className="text-[10px] text-slate-400 leading-tight mt-0.5">{st.desc}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Stream Terminal Logs */}
      <div className="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        <div className="px-4 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-brand-400" />
            <span className="text-xs font-mono font-medium text-slate-300">Live Agent Stream Activity</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-700 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-slate-700 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-slate-700 inline-block" />
          </div>
        </div>
        <div className="p-4 font-mono text-xs text-slate-300 space-y-1.5 max-h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <div className="text-slate-500 italic">Listening for agent notifications...</div>
          ) : (
            logs.map((log, idx) => (
              <div key={idx} className="flex items-start space-x-2 leading-relaxed">
                <span className="text-slate-500 shrink-0">[{log.timestamp}]</span>
                <span className="text-brand-400 shrink-0">❯</span>
                <span className={log.message.includes('completed') ? 'text-emerald-300 font-semibold' : 'text-slate-200'}>
                  {log.message}
                </span>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
};
