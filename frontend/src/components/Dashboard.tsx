import React from 'react';
import {
  Compass,
  Plus,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileText,
  Search,
  Sparkles,
  Layers,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import { ResearchJob, ObservabilityStats } from '../types';

interface DashboardProps {
  jobs: ResearchJob[];
  stats: ObservabilityStats | null;
  onOpenNewResearch: () => void;
  onSelectJob: (job: ResearchJob, view: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  jobs,
  stats,
  onOpenNewResearch,
  onSelectJob,
}) => {
  const getStatusPill = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center space-x-1 text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded text-[11px] font-semibold">
            <CheckCircle2 className="w-3 h-3" />
            <span>Completed</span>
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center space-x-1 text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded text-[11px] font-semibold">
            <AlertCircle className="w-3 h-3" />
            <span>Failed</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 text-brand-400 bg-brand-500/10 border border-brand-500/20 px-2 py-0.5 rounded text-[11px] font-semibold">
            <Clock className="w-3 h-3 animate-spin" />
            <span className="capitalize">{status.replace('_', ' ')}</span>
          </span>
        );
    }
  };

  const samplePrompts = [
    { title: 'Indian AI Startup Ecosystem', query: 'Analyze the Indian AI startup ecosystem and identify the most promising companies.' },
    { title: 'AI Chip War: NVIDIA vs AMD vs Intel', query: 'Compare NVIDIA, AMD and Intel in the AI chip market.' },
    { title: 'Cybersecurity of Autonomous Agents', query: 'Analyze the cybersecurity risks of autonomous AI agents.' },
    { title: 'Cloud AI Platforms: AWS vs Azure vs GCP', query: 'Compare AWS, Azure and Google Cloud for an AI startup.' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Hero Welcome Banner */}
      <div className="relative rounded-3xl bg-gradient-to-r from-slate-900 via-slate-850 to-brand-950 border border-slate-800 p-8 sm:p-10 shadow-2xl overflow-hidden">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center space-x-2 bg-brand-500/15 border border-brand-500/30 px-3 py-1 rounded-full text-brand-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Multi-Agent Research System</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Comprehensive Intelligence. <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-teal-300">
              Corroborated by Independent Evidence.
            </span>
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Deconstruct complex industry inquiries into orchestrated research workflows. Automatically retrieve, verify, cross-check claims, detect conflicting data, and publish citation-backed reports.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={onOpenNewResearch}
              className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white text-xs font-semibold shadow-lg shadow-brand-600/30 transition active:scale-[0.98]"
            >
              <Plus className="w-4 h-4 stroke-[2.5]" />
              <span>Launch New Investigation</span>
            </button>
          </div>
        </div>
      </div>

      {/* Quick Launch Cards */}
      <div>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
          Curated Benchmark Investigations
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {samplePrompts.map((p, idx) => (
            <div
              key={idx}
              onClick={onOpenNewResearch}
              className="bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-brand-500/50 p-4 rounded-2xl cursor-pointer transition shadow-md group flex flex-col justify-between"
            >
              <div>
                <div className="text-xs font-bold text-white group-hover:text-brand-300 transition mb-1">
                  {p.title}
                </div>
                <div className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                  {p.query}
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between text-[11px] text-brand-400 font-semibold">
                <span>Investigate</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* KPI Stats Bar */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-lg">
            <div className="text-[11px] text-slate-400 font-medium">Completed Jobs</div>
            <div className="text-xl font-bold text-white font-mono mt-0.5">{stats.completed_jobs} / {stats.total_jobs}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-lg">
            <div className="text-[11px] text-slate-400 font-medium">Average Latency</div>
            <div className="text-xl font-bold text-white font-mono mt-0.5">{stats.avg_duration_seconds}s</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-lg">
            <div className="text-[11px] text-slate-400 font-medium">Average Quality Score</div>
            <div className="text-xl font-bold text-brand-400 font-mono mt-0.5">{stats.avg_quality_score}/100</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-lg">
            <div className="text-[11px] text-slate-400 font-medium">Average Confidence</div>
            <div className="text-xl font-bold text-emerald-400 font-mono mt-0.5">{Math.round(stats.avg_confidence_score * 100)}%</div>
          </div>
        </div>
      )}

      {/* Previous Research Jobs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Research Investigation History ({jobs.length})
          </h2>
          <button
            onClick={onOpenNewResearch}
            className="text-xs text-brand-400 hover:text-brand-300 font-medium"
          >
            + Start New
          </button>
        </div>

        {jobs.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs italic">
            No research jobs recorded. Click "Launch New Investigation" to begin.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-3">Inquiry</th>
                  <th className="py-3 px-3">Depth</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Progress</th>
                  <th className="py-3 px-3">Initiated</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-850/60 transition">
                    <td className="py-3 px-3 font-semibold text-slate-100 max-w-sm">
                      <div className="truncate">{job.research_question}</div>
                      <div className="text-[10px] text-slate-500 font-mono truncate">{job.current_step}</div>
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-[10px] uppercase font-semibold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                        {job.depth}
                      </span>
                    </td>
                    <td className="py-3 px-3">{getStatusPill(job.status)}</td>
                    <td className="py-3 px-3">
                      <div className="w-24 bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                        <div
                          className="bg-brand-500 h-full rounded-full"
                          style={{ width: `${job.progress_pct}%` }}
                        />
                      </div>
                    </td>
                    <td className="py-3 px-3 text-slate-400 whitespace-nowrap">
                      {new Date(job.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-3 text-right space-x-2 whitespace-nowrap">
                      {job.status === 'completed' ? (
                        <>
                          <button
                            onClick={() => onSelectJob(job, 'report')}
                            className="text-xs font-semibold text-brand-400 hover:text-brand-300 px-2.5 py-1 bg-brand-500/10 rounded-lg hover:bg-brand-500/20 transition"
                          >
                            Report
                          </button>
                          <button
                            onClick={() => onSelectJob(job, 'graph')}
                            className="text-xs font-semibold text-slate-400 hover:text-slate-200 px-2.5 py-1 bg-slate-800 rounded-lg hover:bg-slate-700 transition"
                          >
                            Graph
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={() => onSelectJob(job, 'progress')}
                          className="text-xs font-semibold text-amber-400 hover:text-amber-300 px-2.5 py-1 bg-amber-500/10 rounded-lg hover:bg-amber-500/20 transition"
                        >
                          Live Progress
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
