import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function Overview() {
  const [kpis, setKpis] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [kpiRes, trendRes] = await Promise.all([
          api.get('/dashboard/kpis'),
          api.get('/dashboard/trends?metric=spend_by_vendor')
        ]);
        setKpis(kpiRes.data);
        setTrends(trendRes.data.series);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <div>Loading dashboard telemetry...</div>;

  return (
    <div>
      <div className="header-bar">
        <h1 className="page-title">Executive Intelligence Overview</h1>
      </div>

      {kpis && (
        <div className="grid-kpis">
          <div className="card">
            <div className="kpi-title">Total Documents Processed</div>
            <div className="kpi-val">{kpis.volume.total_processed}</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--accent-emerald)', marginTop: '0.25rem' }}>
              Auto-Accepted: {kpis.volume.auto_accepted} ({kpis.classification_health.auto_accept_rate}%)
            </div>
          </div>
          <div className="card">
            <div className="kpi-title">Auto-Accept Accuracy Rate</div>
            <div className="kpi-val" style={{ color: 'var(--accent-emerald)' }}>{kpis.classification_health.auto_accept_rate}%</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              LLM Disambiguations: {kpis.volume.llm_fallback}
            </div>
          </div>
          <div className="card">
            <div className="kpi-title">Open High/Critical Risks</div>
            <div className="kpi-val" style={{ color: 'var(--accent-rose)' }}>
              {kpis.risk_summary.critical + kpis.risk_summary.high}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Medium: {kpis.risk_summary.medium} | Low: {kpis.risk_summary.low}
            </div>
          </div>
          <div className="card">
            <div className="kpi-title">Avg Latency Per Document</div>
            <div className="kpi-val" style={{ color: 'var(--accent-cyan)' }}>
              {kpis.processing_performance.avg_processing_time_sec}s
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Today's Volume: {kpis.processing_performance.total_volume_today}
            </div>
          </div>
        </div>
      )}

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>Spend Distribution by Party / Vendor</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
          {trends.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No spend trend data available yet.</p>
          ) : (
            trends.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span style={{ fontWeight: '500' }}>{item.label}</span>
                <span style={{ fontWeight: '700', color: 'var(--accent-cyan)' }}>${item.value.toLocaleString()}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
