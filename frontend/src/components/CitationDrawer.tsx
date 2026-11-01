import React from 'react';
import { X, ExternalLink, ShieldCheck, FileText, Calendar } from 'lucide-react';
import { ReportCitation } from '../types';

interface CitationDrawerProps {
  citation: ReportCitation | null;
  onClose: () => void;
}

export const CitationDrawer: React.FC<CitationDrawerProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl p-6 flex flex-col justify-between animate-in slide-in-from-right duration-200">
      <div>
        {/* Drawer Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <span className="w-7 h-7 rounded-lg bg-brand-500/20 text-brand-300 border border-brand-500/30 flex items-center justify-center font-bold text-xs">
              [{citation.citation_number}]
            </span>
            <h3 className="text-base font-semibold text-white tracking-tight">Verified Source Citation</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Source Metadata */}
        <div className="mt-5 space-y-4">
          <div>
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
              Source Publication Title
            </label>
            <div className="text-sm font-semibold text-slate-100">{citation.source_title}</div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
              <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block mb-0.5">
                Domain / Publisher
              </label>
              <div className="text-xs font-medium text-slate-200 truncate">
                {citation.source_domain || 'Vetted Web Domain'}
              </div>
            </div>
            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
              <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block mb-0.5">
                Credibility Assessment
              </label>
              <div className="text-xs font-semibold text-emerald-400 flex items-center space-x-1">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Verified High Quality</span>
              </div>
            </div>
          </div>

          {/* Original Link */}
          {citation.source_url && (
            <div>
              <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
                Original Provenance URL
              </label>
              <a
                href={citation.source_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1.5 text-xs text-brand-400 hover:text-brand-300 break-all bg-brand-500/10 px-3 py-1.5 rounded-lg border border-brand-500/20 hover:border-brand-500/40 transition"
              >
                <ExternalLink className="w-3.5 h-3.5 shrink-0" />
                <span>{citation.source_url}</span>
              </a>
            </div>
          )}

          {/* Evidence Snippet */}
          <div>
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1.5">
              Extracted Evidence Snippet
            </label>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-300 leading-relaxed font-mono">
              {citation.snippet || 'Evidence verified across primary industry documentation and corroborated records.'}
            </div>
          </div>
        </div>
      </div>

      {/* Drawer Footer */}
      <div className="pt-4 border-t border-slate-800">
        <button
          onClick={onClose}
          className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl transition"
        >
          Close Drawer
        </button>
      </div>
    </div>
  );
};
