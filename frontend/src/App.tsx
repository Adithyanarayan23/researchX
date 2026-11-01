import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { LiveProgress } from './components/LiveProgress';
import { ReportViewer } from './components/ReportViewer';
import { EvidenceExplorer } from './components/EvidenceExplorer';
import { ResearchGraphView } from './components/ResearchGraphView';
import { DocumentsManager } from './components/DocumentsManager';
import { ObservabilityView } from './components/ObservabilityView';
import { NewResearchModal } from './components/NewResearchModal';
import {
  listResearchJobs,
  createResearchJob,
  listDocuments,
  getObservabilityOverview,
  getJobReport,
  getJobClaims,
  getJobGraph,
} from './services/api';
import { ResearchJob, ResearchDepth } from './types';

export function App() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [selectedJob, setSelectedJob] = useState<ResearchJob | null>(null);
  const [isNewResearchModalOpen, setIsNewResearchModalOpen] = useState(false);

  // Queries
  const { data: jobs = [], refetch: refetchJobs } = useQuery({
    queryKey: ['researchJobs'],
    queryFn: listResearchJobs,
    refetchInterval: 3000,
  });

  const { data: documents = [], refetch: refetchDocuments } = useQuery({
    queryKey: ['documents'],
    queryFn: listDocuments,
  });

  const { data: observabilityStats = null, refetch: refetchObservability } = useQuery({
    queryKey: ['observabilityStats'],
    queryFn: getObservabilityOverview,
    refetchInterval: 10000,
  });

  const activeJobId = selectedJob?.id || (jobs.length > 0 ? jobs[0].id : null);

  const { data: currentReport = null } = useQuery({
    queryKey: ['jobReport', activeJobId],
    queryFn: () => (activeJobId ? getJobReport(activeJobId) : Promise.resolve(null)),
    enabled: !!activeJobId,
  });

  const { data: currentClaims = [] } = useQuery({
    queryKey: ['jobClaims', activeJobId],
    queryFn: () => (activeJobId ? getJobClaims(activeJobId) : Promise.resolve([])),
    enabled: !!activeJobId,
  });

  const { data: currentGraph = null } = useQuery({
    queryKey: ['jobGraph', activeJobId],
    queryFn: () => (activeJobId ? getJobGraph(activeJobId) : Promise.resolve(null)),
    enabled: !!activeJobId,
  });

  // Launch job mutation
  const launchMutation = useMutation({
    mutationFn: createResearchJob,
    onSuccess: (newJob) => {
      setSelectedJob(newJob);
      queryClient.invalidateQueries({ queryKey: ['researchJobs'] });
      setActiveTab('progress');
    },
  });

  const handleLaunchResearch = (
    question: string,
    depth: ResearchDepth,
    focusAreas: string[]
  ) => {
    launchMutation.mutate({
      research_question: question,
      depth,
      focus_areas: focusAreas,
    });
  };

  const handleSelectJob = (job: ResearchJob, view: string) => {
    setSelectedJob(job);
    setActiveTab(view);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenNewResearch={() => setIsNewResearchModalOpen(true)}
        activeJobId={selectedJob && selectedJob.status !== 'completed' ? selectedJob.id : null}
      />

      {/* Main Content Body */}
      <main className="flex-1 pb-16">
        {activeTab === 'dashboard' && (
          <Dashboard
            jobs={jobs}
            stats={observabilityStats}
            onOpenNewResearch={() => setIsNewResearchModalOpen(true)}
            onSelectJob={handleSelectJob}
          />
        )}

        {activeTab === 'progress' && (
          <LiveProgress
            job={selectedJob || (jobs.length > 0 ? jobs[0] : null)}
            onViewReport={(jobId) => {
              const matched = jobs.find((j) => j.id === jobId);
              if (matched) setSelectedJob(matched);
              setActiveTab('report');
            }}
          />
        )}

        {activeTab === 'report' && (
          <ReportViewer
            report={currentReport}
            onExploreEvidence={() => setActiveTab('evidence')}
            onViewGraph={() => setActiveTab('graph')}
          />
        )}

        {activeTab === 'evidence' && (
          <EvidenceExplorer claims={currentClaims} />
        )}

        {activeTab === 'graph' && (
          <ResearchGraphView graphData={currentGraph} />
        )}

        {activeTab === 'documents' && (
          <DocumentsManager
            documents={documents}
            onRefresh={() => refetchDocuments()}
          />
        )}

        {activeTab === 'observability' && (
          <ObservabilityView stats={observabilityStats} />
        )}
      </main>

      {/* New Research Modal */}
      <NewResearchModal
        isOpen={isNewResearchModalOpen}
        onClose={() => setIsNewResearchModalOpen(false)}
        onSubmit={handleLaunchResearch}
        documents={documents}
      />
    </div>
  );
}

export default App;
