import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  FileText,
  Download,
  Share2,
  ShieldCheck,
  Award,
  RefreshCw,
  Printer,
  Copy,
  Check,
  ExternalLink,
} from 'lucide-react';
import { Report, ReportCitation } from '../types';
import { CitationDrawer } from './CitationDrawer';

interface ReportViewerProps {
  report: Report | null;
  onExploreEvidence?: () => void;
  onViewGraph?: () => void;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({
  report,
  onExploreEvidence,
  onViewGraph,
}) => {
  const [activeCitation, setActiveCitation] = useState<ReportCitation | null>(null);
  const [copied, setCopied] = useState(false);

  if (!report) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center text-slate-400">
        <FileText className="w-12 h-12 mx-auto text-slate-600 mb-3" />
        <h3 className="text-base font-medium text-slate-300">No Intelligence Report Available</h3>
        <p className="text-xs text-slate-500 mt-1">Select an inquiry from the dashboard or launch a new investigation.</p>
      </div>
    );
  }

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(report.markdown_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([report.markdown_content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ResearchX_Report_${report.job_id.slice(0, 8)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  // Enhance markdown by converting citation markers [1], [2] to interactive clickable pills
  const renderInteractiveMarkdown = (content: string) => {
    // Regex for citation anchor [1], [2]
    return (
      <ReactMarkdown
        components={{
          text: ({ node, ...props }) => {
            const rawText = props.children as string;
            if (typeof rawText !== 'string') return <span>{rawText}</span>;

            const parts = rawText.split(/(\[\d+\])/g);
            return (
              <span>
                {parts.map((part, i) => {
                  const match = part.match(/^\[(\d+)\]$/);
                  if (match) {
                    const citNum = parseInt(match[1], 10);
                    const citObj = report.citations.find((c) => c.citation_number === citNum);
                    return (
                      <button
                        key={i}
                        type="button"
                        onClick={() => citObj && setActiveCitation(citObj)}
                        title={citObj ? `Source: ${citObj.source_title}` : `Citation [${citNum}]`}
                        className="inline-flex items-center justify-center font-bold font-mono text-[11px] text-brand-400 hover:text-white bg-brand-500/15 hover:bg-brand-500 border border-brand-500/30 hover:border-brand-400 px-1.5 py-0.2 rounded mx-0.5 transition cursor-pointer"
                      >
                        [{citNum}]
                      </button>
                    );
                  }
                  return <span key={i}>{part}</span>;
                })}
              </span>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Top Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-[11px] font-semibold bg-brand-500/15 text-brand-300 border border-brand-500/30 px-2.5 py-0.5 rounded-full">
                INTELLIGENCE SYNTHESIS
              </span>
              <span className="text-[11px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full flex items-center space-x-1">
                <ShieldCheck className="w-3 h-3" />
                <span>QA Passed: {report.quality_score}/100</span>
              </span>
              {report.revision_count > 0 && (
                <span className="text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full flex items-center space-x-1">
                  <RefreshCw className="w-2.5 h-2.5" />
                  <span>Revision #{report.revision_count}</span>
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">{report.title}</h1>
            <p className="text-xs text-slate-400 mt-1">Generated: {new Date(report.created_at).toLocaleString()}</p>
          </div>

          {/* Action Toolbar */}
          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={handleCopyMarkdown}
              className="flex items-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl border border-slate-700 transition"
              title="Copy Markdown"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl border border-slate-700 transition"
              title="Download Markdown"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export</span>
            </button>
            <button
              onClick={handlePrint}
              className="flex items-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl border border-slate-700 transition"
              title="Print Report"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print</span>
            </button>
          </div>
        </div>

        {/* Epistemic Legend */}
        <div className="flex flex-wrap items-center gap-3 pt-4 text-xs text-slate-400">
          <span className="font-semibold uppercase tracking-wider text-[10px] text-slate-500">Epistemic Grading:</span>
          <span className="inline-flex items-center space-x-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[11px] font-semibold">
            <span>FACT</span>
            <span className="text-slate-400 text-[10px] font-normal">— Corroborated by independent sources</span>
          </span>
          <span className="inline-flex items-center space-x-1 bg-brand-500/10 text-brand-400 border border-brand-500/20 px-2 py-0.5 rounded text-[11px] font-semibold">
            <span>INFERENCE</span>
            <span className="text-slate-400 text-[10px] font-normal">— Deductive logical conclusion</span>
          </span>
          <span className="inline-flex items-center space-x-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded text-[11px] font-semibold">
            <span>SPECULATION</span>
            <span className="text-slate-400 text-[10px] font-normal">— Unconfirmed hypothesis</span>
          </span>
        </div>
      </div>

      {/* Main Report Body */}
      <article className="bg-slate-900 border border-slate-800 rounded-2xl p-8 sm:p-10 shadow-2xl report-content">
        {renderInteractiveMarkdown(report.markdown_content)}
      </article>

      {/* Citations Footer Table */}
      {report.citations.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-brand-400" />
            <span>Vetted Research Citations Directory ({report.citations.length})</span>
          </h3>
          <div className="divide-y divide-slate-800">
            {report.citations.map((c) => (
              <div
                key={c.citation_number}
                onClick={() => setActiveCitation(c)}
                className="py-3 flex items-start justify-between gap-4 cursor-pointer hover:bg-slate-800/40 px-3 rounded-lg transition"
              >
                <div className="flex items-start space-x-3">
                  <span className="font-mono font-bold text-xs text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded border border-brand-500/20 shrink-0">
                    [{c.citation_number}]
                  </span>
                  <div>
                    <div className="text-xs font-semibold text-slate-100 hover:text-brand-300 transition">
                      {c.source_title}
                    </div>
                    <div className="text-[11px] text-slate-400">{c.source_domain || 'Internal Document'}</div>
                  </div>
                </div>
                {c.source_url && (
                  <a
                    href={c.source_url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-slate-400 hover:text-brand-400 p-1"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citation Fly-out Drawer */}
      <CitationDrawer citation={activeCitation} onClose={() => setActiveCitation(null)} />
    </div>
  );
};
