import React from 'react';
import {
  Cpu,
  Clock,
  DollarSign,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { ObservabilityStats } from '../types';

interface ObservabilityViewProps {
  stats: ObservabilityStats | null;
}

export const ObservabilityView: React.FC<ObservabilityViewProps> = ({ stats }) => {
  if (!stats) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center text-slate-400">
        <Cpu className="w-12 h-12 mx-auto text-slate-600 mb-3" />
        <h3 className="text-base font-medium text-slate-300">Loading Observability Telemetry...</h3>
      </div>
    );
  }

  // Format data for chart
  const agentChartData = stats.agent_runs.slice(0, 15).map((r, i) => ({
    name: r.agent_name.replace('Agent', ''),
    duration: Math.round(r.duration_ms / 100) / 10,
    tokens: r.output_tokens,
  }));

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-brand-400" />
            <span>Agentic Telemetry & Observability Hub</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time latency metrics, token consumption, quality benchmarks, and execution audit trails.
          </p>
        </div>
        <div className="flex items-center space-x-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1.5 rounded-xl text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Telemetry Active</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Investigations</span>
            <TrendingUp className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{stats.total_jobs}</div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center space-x-1">
            <span>{stats.completed_jobs} successful</span>
            <span>•</span>
            <span className="text-slate-400">{stats.failed_jobs} failed</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg Latency</span>
            <Clock className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{stats.avg_duration_seconds}s</div>
          <div className="text-[11px] text-slate-400 mt-1">Multi-agent LangGraph workflow</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Tokens & Cost</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">
            ${stats.estimated_cost_usd}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {stats.total_tokens_used.toLocaleString()} total tokens consumed
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Quality & Grounding</span>
            <ShieldCheck className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-2xl font-bold text-brand-400 font-mono">
            {stats.avg_quality_score}/100
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Avg Confidence: {Math.round(stats.avg_confidence_score * 100)}%
          </div>
        </div>
      </div>

      {/* Latency Charts */}
      {agentChartData.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Agent Latency & Output Token Profile
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={agentChartData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="duration" name="Duration (s)" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Agent Execution Audit History Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Recent Agent Run Executions ({stats.agent_runs.length})
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Agent</th>
                <th className="py-2.5 px-3">Model</th>
                <th className="py-2.5 px-3">Duration</th>
                <th className="py-2.5 px-3">Input Tokens</th>
                <th className="py-2.5 px-3">Output Tokens</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {stats.agent_runs.map((r) => (
                <tr key={r.id} className="hover:bg-slate-850/60 transition">
                  <td className="py-2.5 px-3 font-semibold text-white">{r.agent_name}</td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">{r.model_name || 'gemini-2.5-flash'}</td>
                  <td className="py-2.5 px-3 font-mono">{(r.duration_ms / 1000).toFixed(2)}s</td>
                  <td className="py-2.5 px-3 font-mono">{r.input_tokens}</td>
                  <td className="py-2.5 px-3 font-mono">{r.output_tokens}</td>
                  <td className="py-2.5 px-3">
                    <span className="inline-flex items-center space-x-1 text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded text-[10px] font-semibold border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>{r.status}</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
