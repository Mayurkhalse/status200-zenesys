import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Eye } from 'lucide-react';
import api from '../services/api';

export default function DocumentsList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/documents');
      setDocuments(res.data.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
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
      fetchDocuments();
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="header-bar">
        <h1 className="page-title">Ingested Documents</h1>
        <label className="btn" style={{ cursor: 'pointer' }}>
          <Upload size={16} />
          <span>{uploading ? 'Processing File...' : 'Upload Document'}</span>
          <input type="file" onChange={handleFileUpload} disabled={uploading} style={{ display: 'none' }} />
        </label>
      </div>

      <div className="card">
        {loading ? (
          <p>Loading documents...</p>
        ) : (
          <table className="table-container">
            <thead>
              <tr>
                <th>Document ID</th>
                <th>Original Name</th>
                <th>Classification</th>
                <th>Decision</th>
                <th>Status</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.document_id}>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{doc.document_id.slice(0, 8)}...</td>
                  <td>{doc.original_filename}</td>
                  <td>
                    <span className="badge badge-info">
                      {doc.classification?.document_type || 'PENDING'}
                    </span>
                  </td>
                  <td>
                    {doc.classification?.decision ? (
                      <span className={`badge ${
                        doc.classification.decision === 'AUTO_ACCEPT' ? 'badge-success' :
                        doc.classification.decision === 'REVIEW_LLM_FALLBACK' ? 'badge-warning' : 'badge-danger'
                      }`}>
                        {doc.classification.decision}
                      </span>
                    ) : '-'}
                  </td>
                  <td>
                    <span className={`badge ${
                      doc.status === 'completed' ? 'badge-success' :
                      doc.status === 'failed' ? 'badge-danger' : 'badge-warning'
                    }`}>
                      {doc.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    {new Date(doc.created_at).toLocaleString()}
                  </td>
                  <td>
                    <button
                      onClick={() => navigate(`/documents/${doc.document_id}`)}
                      className="btn btn-secondary"
                      style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
                    >
                      <Eye size={14} /> View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
