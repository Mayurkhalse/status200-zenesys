import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Save, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function DocumentDetail() {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [extracted, setExtracted] = useState(null);
  const [fieldsJson, setFieldsJson] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [docRes, extRes] = await Promise.all([
          api.get(`/documents/${id}`),
          api.get(`/extracted-documents/${id}`)
        ]);
        setDocument(docRes.data);
        setExtracted(extRes.data);
        setFieldsJson(JSON.stringify(extRes.data.fields, null, 2));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  const handleSaveFields = async () => {
    setSaving(true);
    try {
      const parsedFields = JSON.parse(fieldsJson);
      const res = await api.patch(`/extracted-documents/${id}`, { fields: parsedFields });
      setExtracted(res.data);
      alert('Extracted document fields updated successfully');
    } catch (err) {
      alert('Invalid JSON structure or update error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Loading document verification detail...</div>;

  return (
    <div>
      <div className="header-bar">
        <div>
          <h1 className="page-title">{document?.original_filename}</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>ID: {id}</p>
        </div>
        <button onClick={handleSaveFields} className="btn" disabled={saving}>
          <Save size={16} />
          <span>{saving ? 'Saving Changes...' : 'Save & Confirm Review'}</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Classification & Telemetry</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div>
              <strong style={{ color: 'var(--text-muted)' }}>Class: </strong>
              <span className="badge badge-info">{document?.classification?.document_type || 'N/A'}</span>
            </div>
            <div>
              <strong style={{ color: 'var(--text-muted)' }}>Decision: </strong>
              <span className="badge badge-success">{document?.classification?.decision || 'N/A'}</span>
            </div>
            <div>
              <strong style={{ color: 'var(--text-muted)' }}>Confidence Score: </strong>
              <span>{(document?.classification?.confidence * 100).toFixed(1)}%</span>
            </div>
            <div>
              <strong style={{ color: 'var(--text-muted)' }}>Source: </strong>
              <span>{document?.classification?.source}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Extracted Fields (JSON Schema)</h3>
          <textarea
            value={fieldsJson}
            onChange={(e) => setFieldsJson(e.target.value)}
            rows={16}
            style={{
              width: '100%',
              background: '#090d16',
              border: '1px solid var(--border-color)',
              color: '#fff',
              fontFamily: 'monospace',
              padding: '0.75rem',
              borderRadius: '8px'
            }}
          />
        </div>
      </div>
    </div>
  );
}
