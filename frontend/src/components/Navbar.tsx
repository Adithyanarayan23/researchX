import React from 'react';
import {
  Compass,
  FileText,
  Search,
  Network,
  Activity,
  FolderOpen,
  Plus,
  ShieldCheck,
  Cpu,
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenNewResearch: () => void;
  activeJobId: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenNewResearch,
  activeJobId,
}) => {
  const navItems = [
    { id: 'landing', label: 'Overview', icon: Compass },
    { id: 'dashboard', label: 'Dashboard', icon: Search },
    { id: 'progress', label: 'Live Progress', icon: Activity, badge: activeJobId ? 'Active' : undefined },
    { id: 'report', label: 'Report Viewer', icon: FileText },
    { id: 'evidence', label: 'Evidence & Claims', icon: ShieldCheck },
    { id: 'graph', label: 'Research Graph', icon: Network },
    { id: 'documents', label: 'Documents RAG', icon: FolderOpen },
    { id: 'observability', label: 'Observability', icon: Cpu },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('landing')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Search className="w-5 h-5 text-white stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white">Research<span className="text-brand-400">X</span></span>
              <span className="text-[10px] font-semibold bg-brand-500/20 text-brand-300 border border-brand-500/30 px-1.5 py-0.5 rounded">AGENTIC v1.0</span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Autonomous Multi-Agent Intelligence Platform</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-brand-500/15 text-brand-300 border border-brand-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-brand-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
                {item.badge && (
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-1" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Action Button */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenNewResearch}
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white text-xs font-semibold shadow-md shadow-brand-600/20 transition-all active:scale-[0.98]"
          >
            <Plus className="w-4 h-4 stroke-[2.5]" />
            <span>New Research</span>
          </button>
        </div>
      </div>
    </header>
  );
};
