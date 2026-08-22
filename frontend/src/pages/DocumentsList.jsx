import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Eye, RefreshCw, CheckCircle, AlertTriangle, Clock } from 'lucide-react';
import api from '../services/api';

export default function DocumentsList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const fetchDocuments = async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const res = await api.get('/documents');
      setDocuments(res.data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments(true);

    // Auto-poll every 2.5s to update pipeline statuses while processing
    const interval = setInterval(() => {
      fetchDocuments(false);
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchDocuments(false);
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="header-bar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 className="page-title" style={{ fontSize: '1.6rem', margin: 0 }}>Ingested Documents</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
            Live status of document OCR, classification, and field extraction pipeline.
          </p>
        </div>
        <label className="btn" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Upload size={16} />
          <span>{uploading ? 'Uploading File...' : 'Upload Document'}</span>
          <input type="file" onChange={handleFileUpload} disabled={uploading} style={{ display: 'none' }} />
        </label>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem', color: 'var(--text-muted)' }}>
            <RefreshCw className="animate-spin" size={16} />
            <span>Loading documents...</span>
          </div>
        ) : documents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <FileText size={36} style={{ marginBottom: '0.5rem', opacity: 0.5 }} />
            <p style={{ fontSize: '0.95rem' }}>No documents uploaded yet.</p>
            <p style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>Click "Upload Document" above to process your first invoice, purchase order, or contract.</p>
          </div>
        ) : (
          <table className="table-container">
            <thead>
              <tr>
                <th>Document ID</th>
                <th>Original File</th>
                <th>Document Classification</th>
                <th>Confidence</th>
                <th>Decision Routing</th>
                <th>Pipeline Status</th>
                <th>Uploaded At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => {
                const isProcessing = ['uploaded', 'preprocessing', 'classifying', 'extracting', 'insight_pending'].includes(doc.status);

                return (
                  <tr key={doc.document_id}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--accent-cyan)' }}>
                      {doc.document_id.slice(0, 8)}...
                    </td>
                    <td style={{ fontWeight: '500' }}>{doc.original_filename}</td>
                    <td>
                      <span className="badge badge-info">
                        {doc.classification?.document_type || (isProcessing ? 'CLASSIFYING...' : 'PENDING')}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.85rem', fontWeight: '600' }}>
                      {doc.classification?.confidence ? `${Math.round(doc.classification.confidence * 100)}%` : '-'}
                    </td>
                    <td>
                      {doc.classification?.decision ? (
                        <span className={`badge ${
                          doc.classification.decision === 'AUTO_ACCEPT' ? 'badge-success' :
                          doc.classification.decision === 'REVIEW_LLM_FALLBACK' ? 'badge-warning' : 'badge-warning'
                        }`}>
                          {doc.classification.decision.replace('_', ' ')}
                        </span>
                      ) : '-'}
                    </td>
                    <td>
                      <span className={`badge ${
                        doc.status === 'completed' ? 'badge-success' :
                        doc.status === 'human_review' ? 'badge-warning' :
                        doc.status === 'failed' ? 'badge-danger' : 'badge-info'
                      }`} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                        {isProcessing && <RefreshCw className="animate-spin" size={12} />}
                        {doc.status.toUpperCase().replace('_', ' ')}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      {new Date(doc.created_at).toLocaleString()}
                    </td>
                    <td>
                      <button
                        onClick={() => navigate(`/documents/${doc.document_id}`)}
                        className="btn btn-secondary"
                        style={{ padding: '0.3rem 0.65rem', fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
                      >
                        <Eye size={14} /> View
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
