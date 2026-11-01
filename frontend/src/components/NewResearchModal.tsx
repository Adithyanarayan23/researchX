import React, { useState } from 'react';
import {
  X,
  Sparkles,
  Zap,
  Target,
  Layers,
  ArrowRight,
  FileCheck,
  CheckCircle2,
} from 'lucide-react';
import { ResearchDepth, DocumentItem } from '../types';

interface NewResearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (question: string, depth: ResearchDepth, focusAreas: string[]) => void;
  documents: DocumentItem[];
}

export const NewResearchModal: React.FC<NewResearchModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  documents,
}) => {
  const [question, setQuestion] = useState('');
  const [depth, setDepth] = useState<ResearchDepth>('standard');
  const [selectedFocus, setSelectedFocus] = useState<string[]>([]);
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);

  if (!isOpen) return null;

  const sampleQueries = [
    'Analyze the Indian AI startup ecosystem and identify the most promising companies.',
    'Compare NVIDIA, AMD and Intel in the AI chip market.',
    'Research the impact of generative AI on software engineering jobs.',
    'Analyze the cybersecurity risks of autonomous AI agents.',
    'Compare AWS, Azure and Google Cloud for an AI startup.',
  ];

  const focusOptions = [
    'Financial Performance',
    'Architectural Moats',
    'Competitive Dynamics',
    'Enterprise Adoption',
    'Regulatory Risks',
    'Hardware Benchmarks',
  ];

  const handleToggleFocus = (area: string) => {
    setSelectedFocus((prev) =>
      prev.includes(area) ? prev.filter((a) => a !== area) : [...prev, area]
    );
  };

  const handleLaunch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    onSubmit(question, depth, selectedFocus);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-brand-400" />
            <h2 className="text-lg font-semibold text-white tracking-tight">Initiate Autonomous Investigation</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleLaunch} className="p-6 space-y-6">
          {/* Main Question Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              What complex inquiry would you like to investigate?
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Compare NVIDIA, AMD and Intel in the AI accelerator market..."
              rows={3}
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition resize-none"
            />
          </div>

          {/* Quick Preset Queries */}
          <div>
            <span className="text-[11px] font-medium text-slate-400 block mb-1.5">Preset Inquiries:</span>
            <div className="flex flex-wrap gap-1.5">
              {sampleQueries.map((q, idx) => (
                <button
                  type="button"
                  key={idx}
                  onClick={() => setQuestion(q)}
                  className="text-left text-[11px] bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-brand-300 border border-slate-700/60 px-2.5 py-1 rounded-md transition line-clamp-1"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Research Depth Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Research Depth
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'quick', label: 'Quick', icon: Zap, tasks: '3-4 subtasks', time: '~30-45s', desc: 'Rapid initial overview' },
                { id: 'standard', label: 'Standard', icon: Target, tasks: '5-7 subtasks', time: '~1-2 min', desc: 'Corroboration & RAG' },
                { id: 'deep', label: 'Deep', icon: Layers, tasks: '8-10 subtasks', time: '~3-4 min', desc: 'Conflict analysis' },
              ].map((lvl) => {
                const Icon = lvl.icon;
                const isSelected = depth === lvl.id;
                return (
                  <div
                    key={lvl.id}
                    onClick={() => setDepth(lvl.id as ResearchDepth)}
                    className={`cursor-pointer p-3 rounded-xl border transition-all text-left ${
                      isSelected
                        ? 'border-brand-500 bg-brand-500/10 shadow-sm'
                        : 'border-slate-800 bg-slate-950/60 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <Icon className={`w-4 h-4 ${isSelected ? 'text-brand-400' : 'text-slate-400'}`} />
                      {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-brand-400" />}
                    </div>
                    <div className="text-sm font-semibold text-slate-200">{lvl.label}</div>
                    <div className="text-[11px] text-slate-400">{lvl.tasks}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Focus Areas Tags */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Optional Focus Dimensions
            </label>
            <div className="flex flex-wrap gap-2">
              {focusOptions.map((area) => {
                const active = selectedFocus.includes(area);
                return (
                  <button
                    type="button"
                    key={area}
                    onClick={() => handleToggleFocus(area)}
                    className={`text-xs px-2.5 py-1 rounded-lg border transition ${
                      active
                        ? 'bg-brand-500/20 text-brand-300 border-brand-500/40'
                        : 'bg-slate-950/40 text-slate-400 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    {area}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Footer Action */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!question.trim()}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-brand-600/30 transition active:scale-[0.98]"
            >
              <span>Dispatch Multi-Agent Workflow</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
