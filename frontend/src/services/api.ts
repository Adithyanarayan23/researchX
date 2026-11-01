import {
  ResearchJob,
  ResearchTask,
  Source,
  Claim,
  Finding,
  Report,
  ResearchGraphData,
  DocumentItem,
  ObservabilityStats,
  ResearchDepth,
} from '../types';

const API_BASE = '/api';

export async function createResearchJob(payload: {
  research_question: string;
  depth?: ResearchDepth;
  document_ids?: string[];
  focus_areas?: string[];
}): Promise<ResearchJob> {
  const res = await fetch(`${API_BASE}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create research job');
  }
  return res.json();
}

export async function listResearchJobs(): Promise<ResearchJob[]> {
  const res = await fetch(`${API_BASE}/research`);
  if (!res.ok) throw new Error('Failed to fetch research jobs');
  return res.json();
}

export async function getResearchJob(jobId: string): Promise<ResearchJob> {
  const res = await fetch(`${API_BASE}/research/${jobId}`);
  if (!res.ok) throw new Error('Failed to fetch research job');
  return res.json();
}

export async function getJobTasks(jobId: string): Promise<ResearchTask[]> {
  const res = await fetch(`${API_BASE}/research/${jobId}/tasks`);
  if (!res.ok) throw new Error('Failed to fetch tasks');
  return res.json();
}

export async function getJobSources(jobId: string): Promise<Source[]> {
  const res = await fetch(`${API_BASE}/research/${jobId}/sources`);
  if (!res.ok) throw new Error('Failed to fetch sources');
  return res.json();
}

export async function getJobClaims(jobId: string): Promise<Claim[]> {
  const res = await fetch(`${API_BASE}/research/${jobId}/claims`);
  if (!res.ok) throw new Error('Failed to fetch claims');
  return res.json();
}

export async function getJobFindings(jobId: string): Promise<Finding[]> {
  const res = await fetch(`${API_BASE}/research/${jobId}/findings`);
  if (!res.ok) throw new Error('Failed to fetch findings');
  return res.json();
}

export async function getJobReport(jobId: string): Promise<Report> {
  const res = await fetch(`${API_BASE}/research/${jobId}/report`);
  if (!res.ok) throw new Error('Failed to fetch report');
  return res.json();
}

export async function getJobGraph(jobId: string): Promise<ResearchGraphData> {
  const res = await fetch(`${API_BASE}/research/${jobId}/graph`);
  if (!res.ok) throw new Error('Failed to fetch research graph');
  return res.json();
}

export async function cancelJob(jobId: string): Promise<void> {
  await fetch(`${API_BASE}/research/${jobId}/cancel`, { method: 'POST' });
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload document');
  }
  return res.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete document');
}

export async function searchDocuments(query: string, topK: number = 5): Promise<any[]> {
  const res = await fetch(`${API_BASE}/documents/search?query=${encodeURIComponent(query)}&top_k=${topK}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to search documents');
  return res.json();
}

export async function getObservabilityOverview(): Promise<ObservabilityStats> {
  const res = await fetch(`${API_BASE}/observability/overview`);
  if (!res.ok) throw new Error('Failed to fetch observability metrics');
  return res.json();
}
