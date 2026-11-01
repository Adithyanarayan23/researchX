export type ResearchDepth = 'quick' | 'standard' | 'deep';

export type JobStatus =
  | 'queued'
  | 'planning'
  | 'researching'
  | 'verifying'
  | 'analyzing'
  | 'generating_report'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface ResearchJob {
  id: string;
  title: string;
  research_question: string;
  depth: ResearchDepth;
  status: JobStatus;
  progress_pct: number;
  current_step: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ResearchTask {
  id: string;
  title: string;
  category: string;
  description?: string;
  status: string;
  order_index: number;
}

export interface Source {
  id: string;
  url?: string;
  title: string;
  domain?: string;
  publisher?: string;
  published_at?: string;
  retrieved_at: string;
  source_type: string;
  credibility_score: number;
  content_snippet?: string;
}

export interface ClaimEvidence {
  id: string;
  source_id: string;
  source_title?: string;
  source_url?: string;
  snippet: string;
  relevance_score: number;
  is_supporting: boolean;
}

export interface VerificationResult {
  status: 'verified' | 'partially_verified' | 'conflicting' | 'unsupported' | 'unverifiable';
  confidence_score: number;
  reasoning_summary?: string;
  conflicting_notes?: string;
}

export interface Claim {
  id: string;
  claim_text: string;
  claim_type: string;
  importance: string;
  verification?: VerificationResult;
  evidence: ClaimEvidence[];
}

export interface Finding {
  id: string;
  title: string;
  statement: string;
  category: 'FACT' | 'INFERENCE' | 'SPECULATION';
  confidence_score: number;
  confidence_tier: string;
  evidence_count: number;
  order_index: number;
}

export interface ReportCitation {
  citation_number: number;
  source_id: string;
  source_title: string;
  source_url?: string;
  source_domain?: string;
  snippet?: string;
}

export interface Report {
  id: string;
  job_id: string;
  title: string;
  executive_summary: string;
  markdown_content: string;
  quality_score: number;
  revision_count: number;
  qc_notes?: string;
  citations: ReportCitation[];
  created_at: string;
}

export interface GraphNode {
  id: string;
  type: string;
  data: Record<string, any>;
  position: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated?: boolean;
}

export interface ResearchGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  processed: boolean;
  summary?: string;
  chunks_count: number;
  created_at: string;
}

export interface AgentRun {
  id: string;
  agent_name: string;
  start_time: string;
  end_time?: string;
  duration_ms: number;
  input_tokens: number;
  output_tokens: number;
  model_name?: string;
  tool_calls_count: number;
  status: string;
  error_message?: string;
}

export interface ObservabilityStats {
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  avg_duration_seconds: number;
  total_tokens_used: number;
  estimated_cost_usd: number;
  avg_confidence_score: number;
  avg_quality_score: number;
  agent_runs: AgentRun[];
}
