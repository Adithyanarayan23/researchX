import React, { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Network, Sparkles, Database, ShieldCheck, BarChart3, HelpCircle } from 'lucide-react';
import { ResearchGraphData } from '../types';

interface ResearchGraphViewProps {
  graphData: ResearchGraphData | null;
}

// Custom Node for Research Question
const QuestionNode = ({ data }: any) => (
  <div className="bg-gradient-to-r from-brand-700 to-brand-600 border-2 border-brand-400 p-4 rounded-xl text-white shadow-2xl max-w-sm">
    <div className="flex items-center space-x-1.5 text-[10px] font-bold uppercase tracking-wider text-brand-200 mb-1">
      <Sparkles className="w-3.5 h-3.5" />
      <span>Primary Research Question</span>
    </div>
    <div className="text-xs font-semibold leading-snug">{data.label}</div>
    <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-brand-300" />
  </div>
);

// Custom Node for Sub-Task
const TaskNode = ({ data }: any) => (
  <div className="bg-slate-900 border border-slate-700 p-3 rounded-xl text-slate-100 shadow-lg max-w-xs">
    <Handle type="target" position={Position.Top} className="w-2 h-2 bg-slate-400" />
    <div className="text-[10px] uppercase font-bold text-teal-400 mb-0.5">Task: {data.category}</div>
    <div className="text-xs font-medium line-clamp-2 leading-tight">{data.label}</div>
    <Handle type="source" position={Position.Bottom} className="w-2 h-2 bg-teal-400" />
  </div>
);

// Custom Node for Source
const SourceNode = ({ data }: any) => (
  <div className="bg-slate-900/90 border border-emerald-500/40 p-2.5 rounded-xl text-slate-200 shadow-md max-w-[200px]">
    <Handle type="target" position={Position.Top} className="w-2 h-2 bg-emerald-400" />
    <div className="flex items-center space-x-1 text-[9px] uppercase font-bold text-emerald-400 mb-0.5">
      <Database className="w-3 h-3" />
      <span className="truncate">{data.domain || 'Source'}</span>
    </div>
    <div className="text-[11px] font-medium truncate text-slate-100">{data.label}</div>
    <Handle type="source" position={Position.Bottom} className="w-2 h-2 bg-emerald-400" />
  </div>
);

// Custom Node for Claim
const ClaimNode = ({ data }: any) => (
  <div className="bg-slate-900 border border-amber-500/40 p-2.5 rounded-xl text-slate-200 shadow-md max-w-[220px]">
    <Handle type="target" position={Position.Top} className="w-2 h-2 bg-amber-400" />
    <div className="flex items-center justify-between text-[9px] font-bold uppercase text-amber-400 mb-0.5">
      <span>{data.status}</span>
      <span>{Math.round((data.confidence || 0.8) * 100)}%</span>
    </div>
    <div className="text-[11px] font-medium line-clamp-2 leading-tight text-slate-100">{data.label}</div>
    <Handle type="source" position={Position.Bottom} className="w-2 h-2 bg-amber-400" />
  </div>
);

// Custom Node for Finding
const FindingNode = ({ data }: any) => (
  <div className="bg-gradient-to-tr from-indigo-950 to-slate-900 border border-indigo-500/50 p-3 rounded-xl text-slate-100 shadow-lg max-w-xs">
    <Handle type="target" position={Position.Top} className="w-2 h-2 bg-indigo-400" />
    <div className="flex items-center space-x-1 text-[10px] font-bold uppercase text-indigo-400 mb-0.5">
      <BarChart3 className="w-3 h-3" />
      <span>{data.category} FINDING</span>
    </div>
    <div className="text-xs font-semibold text-white leading-snug">{data.label}</div>
  </div>
);

export const ResearchGraphView: React.FC<ResearchGraphViewProps> = ({ graphData }) => {
  const nodeTypes = useMemo(
    () => ({
      question: QuestionNode,
      task: TaskNode,
      source: SourceNode,
      claim: ClaimNode,
      finding: FindingNode,
    }),
    []
  );

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center text-slate-400">
        <Network className="w-12 h-12 mx-auto text-slate-600 mb-3" />
        <h3 className="text-base font-medium text-slate-300">No Graph Lineage Available</h3>
        <p className="text-xs text-slate-500 mt-1">Select an active or completed research job to inspect lineage.</p>
      </div>
    );
  }

  // Format nodes and edges for React Flow
  const formattedNodes: Node[] = graphData.nodes.map((n) => ({
    id: n.id,
    type: n.type,
    position: n.position,
    data: n.data,
  }));

  const formattedEdges: Edge[] = graphData.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    animated: e.animated,
    style: { stroke: '#0284c7', strokeWidth: 1.5 },
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-4">
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 p-4 rounded-2xl shadow-xl">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight flex items-center space-x-2">
            <Network className="w-5 h-5 text-brand-400" />
            <span>Interactive Multi-Agent Lineage Graph</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Trace the lineage from Research Question → Tasks → Sources → Claims → Verification → Findings.
          </p>
        </div>
      </div>

      <div className="w-full h-[650px] bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl relative">
        <ReactFlow
          nodes={formattedNodes}
          edges={formattedEdges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.2}
          maxZoom={1.5}
        >
          <Background color="#1e293b" gap={20} size={1} />
          <Controls className="bg-slate-900 border-slate-800 text-white fill-white" />
          <MiniMap
            nodeStrokeColor="#38bdf8"
            nodeColor="#0f172a"
            maskColor="rgba(8, 13, 26, 0.7)"
            className="bg-slate-950 border border-slate-800 rounded-lg"
          />
        </ReactFlow>
      </div>
    </div>
  );
};
