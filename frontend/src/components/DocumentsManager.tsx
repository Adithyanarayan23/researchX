import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  Trash2,
  Search,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles,
} from 'lucide-react';
import { DocumentItem } from '../types';
import { uploadDocument, deleteDocument, searchDocuments } from '../services/api';

interface DocumentsManagerProps {
  documents: DocumentItem[];
  onRefresh: () => void;
}

export const DocumentsManager: React.FC<DocumentsManagerProps> = ({
  documents,
  onRefresh,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);
    try {
      await uploadDocument(file);
      onRefresh();
    } catch (err: any) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document and its vector embeddings?')) return;
    try {
      await deleteDocument(id);
      onRefresh();
    } catch (err) {
      //
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const results = await searchDocuments(searchQuery, 4);
      setSearchResults(results);
    } catch (err) {
      //
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Upload Zone Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h2 className="text-xl font-bold text-white tracking-tight mb-1 flex items-center space-x-2">
          <Layers className="w-5 h-5 text-brand-400" />
          <span>Document Intelligence & pgvector RAG Repository</span>
        </h2>
        <p className="text-xs text-slate-400 mb-6">
          Upload proprietary whitepapers, financial reports, and regulatory filings for hybrid semantic and keyword retrieval.
        </p>

        {/* Dropzone */}
        <label className="border-2 border-dashed border-slate-700 hover:border-brand-500 rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer bg-slate-950/40 hover:bg-slate-950/80 transition group">
          <UploadCloud className="w-10 h-10 text-slate-400 group-hover:text-brand-400 mb-2 transition" />
          <span className="text-sm font-semibold text-slate-200">
            {isUploading ? 'Ingesting and vectorizing chunks...' : 'Click to select or drag document'}
          </span>
          <span className="text-xs text-slate-500 mt-1">Supported formats: PDF, DOCX, TXT, MD (Max 20MB)</span>
          <input
            type="file"
            onChange={handleFileUpload}
            disabled={isUploading}
            accept=".pdf,.docx,.doc,.txt,.md"
            className="hidden"
          />
        </label>
        {uploadError && (
          <div className="mt-3 text-xs text-rose-400 font-medium">{uploadError}</div>
        )}
      </div>

      {/* Indexed Documents Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Indexed Documents ({documents.length})
        </h3>
        {documents.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs italic">
            No external documents uploaded yet.
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {documents.map((doc) => (
              <div key={doc.id} className="py-3.5 flex items-center justify-between gap-4">
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-lg bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-100">{doc.filename}</div>
                    <div className="text-[11px] text-slate-400 flex items-center space-x-2 mt-0.5">
                      <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                      <span>•</span>
                      <span className="font-mono text-brand-400 font-semibold">{doc.chunks_count} chunks embedded</span>
                      <span>•</span>
                      <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center space-x-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Indexed</span>
                  </span>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Interactive Hybrid RAG Search Test Sandbox */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span>Hybrid Retrieval Sandbox (0.65 Vector + 0.25 Keyword + 0.10 Quality)</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Test real-time semantic vector similarity and keyword density scores across indexed document chunks.
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Enter query to test hybrid retrieval scores..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
          <button
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
            className="px-4 py-2.5 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold transition"
          >
            {isSearching ? 'Scoring...' : 'Execute Search'}
          </button>
        </form>

        {searchResults.length > 0 && (
          <div className="space-y-3 pt-2">
            <div className="text-xs font-semibold text-slate-400">Top Retrieved Chunks:</div>
            {searchResults.map((r, i) => (
              <div key={i} className="bg-slate-950 border border-slate-800 p-3.5 rounded-xl text-xs space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
                  <span className="font-semibold text-brand-400">
                    Chunk #{r.metadata?.chunk_index ?? i + 1} ({r.metadata?.section || 'Document Section'})
                  </span>
                  <div className="flex items-center space-x-2 font-mono text-[11px]">
                    <span className="text-emerald-400">Final: {r.final_score}</span>
                    <span className="text-slate-500">|</span>
                    <span className="text-brand-300">Sem: {r.semantic_score}</span>
                    <span className="text-slate-500">|</span>
                    <span className="text-amber-300">Key: {r.keyword_score}</span>
                  </div>
                </div>
                <p className="text-slate-300 font-mono text-[11px] leading-relaxed">
                  "{r.content}"
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
