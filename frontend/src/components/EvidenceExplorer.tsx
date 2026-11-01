import React, { useState } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  CheckCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Filter,
} from 'lucide-react';
import { Claim } from '../types';

interface EvidenceExplorerProps {
  claims: Claim[];
}

export const EvidenceExplorer: React.FC<EvidenceExplorerProps> = ({ claims }) => {
  const [filter, setFilter] = useState<string>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const filteredClaims = claims.filter((c) => {
    if (filter === 'all') return true;
    const status = c.verification?.status || 'unverified';
    return status === filter;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'verified':
        return (
          <span className="inline-flex items-center space-x-1 bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded text-[11px] font-semibold">
            <CheckCircle className="w-3 h-3" />
            <span>Verified</span>
          </span>
        );
      case 'partially_verified':
        return (
          <span className="inline-flex items-center space-x-1 bg-brand-500/15 text-brand-300 border border-brand-500/30 px-2 py-0.5 rounded text-[11px] font-semibold">
            <CheckCircle className="w-3 h-3" />
            <span>Partially Verified</span>
          </span>
        );
      case 'conflicting':
        return (
          <span className="inline-flex items-center space-x-1 bg-amber-500/15 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded text-[11px] font-semibold">
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            <span>Conflicting Data</span>
          </span>
        );
      case 'unsupported':
      default:
        return (
          <span className="inline-flex items-center space-x-1 bg-rose-500/15 text-rose-300 border border-rose-500/30 px-2 py-0.5 rounded text-[11px] font-semibold">
            <HelpCircle className="w-3 h-3" />
            <span>Unsupported</span>
          </span>
        );
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Header and Filter */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-brand-400" />
            <span>Claim Verification & Evidence Explorer</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Every factual claim is mapped to primary evidence snippets with independent corroboration.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
          {['all', 'verified', 'conflicting', 'partially_verified', 'unsupported'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-lg text-xs font-medium capitalize transition ${
                filter === f
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {f.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Claims List */}
      <div className="space-y-3">
        {filteredClaims.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
            <ShieldCheck className="w-10 h-10 mx-auto text-slate-600 mb-2" />
            <p className="text-sm font-medium">No claims match the selected filter.</p>
          </div>
        ) : (
          filteredClaims.map((claim) => {
            const isExpanded = expandedId === claim.id;
            const status = claim.verification?.status || 'unverified';
            const confidence = claim.verification?.confidence_score || 0.5;
            const confPct = Math.round(confidence * 100);

            return (
              <div
                key={claim.id}
                className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-lg transition"
              >
                {/* Header Row */}
                <div
                  onClick={() => toggleExpand(claim.id)}
                  className="p-5 flex items-start justify-between gap-4 cursor-pointer hover:bg-slate-850/60 transition"
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      {getStatusBadge(status)}
                      <span className="text-[10px] uppercase font-semibold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                        {claim.claim_type}
                      </span>
                      <span className="text-[10px] uppercase font-semibold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                        {claim.importance} Priority
                      </span>
                    </div>
                    <div className="text-sm font-medium text-slate-100 leading-snug">
                      "{claim.claim_text}"
                    </div>
                  </div>

                  {/* Confidence Metric & Expand */}
                  <div className="flex items-center space-x-4 shrink-0">
                    <div className="text-right">
                      <div className="text-[10px] text-slate-400 font-medium">Confidence</div>
                      <div className="text-xs font-bold text-brand-400 font-mono">{confPct}%</div>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-5 pb-5 pt-2 border-t border-slate-800 bg-slate-950/40 space-y-4">
                    {/* Conflict Alert if applicable */}
                    {claim.verification?.conflicting_notes && (
                      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3.5 text-xs text-amber-200">
                        <div className="flex items-center space-x-2 font-bold mb-1 text-amber-400">
                          <AlertTriangle className="w-4 h-4" />
                          <span>CONFLICT DETECTED BETWEEN INDEPENDENT SOURCES</span>
                        </div>
                        <p>{claim.verification.conflicting_notes}</p>
                      </div>
                    )}

                    {/* Reasoning Summary */}
                    {claim.verification?.reasoning_summary && (
                      <div>
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                          Auditor Reasoning Summary
                        </div>
                        <div className="text-xs text-slate-300 leading-relaxed bg-slate-900 p-3 rounded-xl border border-slate-800">
                          {claim.verification.reasoning_summary}
                        </div>
                      </div>
                    )}

                    {/* Evidence Snippets */}
                    <div>
                      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
                        Supporting Evidence Items ({claim.evidence.length})
                      </div>
                      <div className="space-y-2">
                        {claim.evidence.map((ev, idx) => (
                          <div
                            key={idx}
                            className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs space-y-1.5"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-brand-300">
                                {ev.source_title || 'Corroborating Source'}
                              </span>
                              {ev.source_url && (
                                <a
                                  href={ev.source_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="text-slate-400 hover:text-brand-400 flex items-center space-x-1 text-[11px]"
                                >
                                  <span>View Source</span>
                                  <ExternalLink className="w-3 h-3" />
                                </a>
                              )}
                            </div>
                            <p className="text-slate-300 font-mono text-[11px] leading-relaxed bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                              "{ev.snippet}"
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
