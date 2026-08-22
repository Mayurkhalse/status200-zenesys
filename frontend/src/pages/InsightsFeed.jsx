import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';
import api from '../services/api';

export default function InsightsFeed() {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchInsights = async () => {
    try {
      const res = await api.get('/insights');
      setInsights(res.data.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const handleUpdateStatus = async (insightId, newStatus) => {
    try {
      await api.patch(`/insights/${insightId}`, { status: newStatus });
      fetchInsights();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  return (
    <div>
      <div className="header-bar">
        <h1 className="page-title">Actionable Risk & Anomaly Insights</h1>
      </div>

      {loading ? (
        <p>Loading AI insight feed...</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {insights.length === 0 ? (
            <div className="card">No open risk flags or anomalies detected.</div>
          ) : (
            insights.map((ins) => (
              <div key={ins.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <span className={`badge ${
                      ins.severity === 'critical' || ins.severity === 'high' ? 'badge-danger' :
                      ins.severity === 'medium' ? 'badge-warning' : 'badge-info'
                    }`}>
                      {ins.severity.toUpperCase()} {ins.type.toUpperCase()}
                    </span>
                    <strong style={{ fontSize: '1rem' }}>{ins.title}</strong>
                  </div>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                    {ins.description}
                  </p>
                  <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
                    Related Entity: {ins.related_entity}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {ins.status === 'open' && (
                    <button
                      onClick={() => handleUpdateStatus(ins.id, 'acknowledged')}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.8rem' }}
                    >
                      Acknowledge
                    </button>
                  )}
                  {ins.status !== 'resolved' && (
                    <button
                      onClick={() => handleUpdateStatus(ins.id, 'resolved')}
                      className="btn"
                      style={{ fontSize: '0.8rem', backgroundColor: 'var(--accent-emerald)' }}
                    >
                      <CheckCircle size={14} /> Resolve
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
