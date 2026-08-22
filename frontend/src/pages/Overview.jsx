import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { 
  TrendingUp, FileText, AlertTriangle, Clock, CheckCircle, 
  Layers, ShieldAlert, Calendar, RefreshCw
} from 'lucide-react';

export default function Overview() {
  const [kpis, setKpis] = useState(null);
  const [datewiseData, setDatewiseData] = useState([]);
  const [spendData, setSpendData] = useState([]);
  const [typeData, setTypeData] = useState([]);
  const [decisionData, setDecisionData] = useState([]);
  const [activeTab, setActiveTab] = useState('datewise');
  const [loading, setLoading] = useState(true);
  const [hoveredPoint, setHoveredPoint] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [kpiRes, datewiseRes, spendRes, typeRes, decisionRes] = await Promise.all([
        api.get('/dashboard/kpis'),
        api.get('/dashboard/trends?metric=datewise_volume'),
        api.get('/dashboard/trends?metric=spend_by_vendor'),
        api.get('/dashboard/trends?metric=volume_by_type'),
        api.get('/dashboard/trends?metric=decision_breakdown')
      ]);

      setKpis(kpiRes.data);
      setDatewiseData(datewiseRes.data.series || []);
      setSpendData(spendRes.data.series || []);
      setTypeData(typeRes.data.series || []);
      setDecisionData(decisionRes.data.series || []);
    } catch (err) {
      console.error("Failed to load dashboard telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: '1rem' }}>
        <RefreshCw className="animate-spin" size={32} style={{ color: 'var(--primary)' }} />
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>Loading live Executive Intelligence telemetry...</p>
      </div>
    );
  }

  const maxDatewiseVal = Math.max(...datewiseData.map(d => d.value), 1);
  const maxSpendVal = Math.max(...spendData.map(d => d.value), 1);
  const totalDocsCount = typeData.reduce((acc, curr) => acc + curr.value, 0) || 1;

  // SVG Line Path calculation for Datewise Area Chart
  const chartHeight = 190;
  const chartWidth = 700;
  const paddingX = 40;
  const paddingY = 25;

  const points = datewiseData.map((item, idx) => {
    const x = paddingX + (idx / Math.max(datewiseData.length - 1, 1)) * (chartWidth - paddingX * 2);
    const y = chartHeight - paddingY - (item.value / maxDatewiseVal) * (chartHeight - paddingY * 2);
    return { x, y, label: item.label, value: item.value };
  });

  const linePathD = points.length > 0 
    ? points.reduce((acc, pt, idx) => `${acc} ${idx === 0 ? 'M' : 'L'} ${pt.x} ${pt.y}`, '')
    : `M ${paddingX} ${chartHeight - paddingY} L ${chartWidth - paddingX} ${chartHeight - paddingY}`;

  const areaPathD = points.length > 0
    ? `${linePathD} L ${points[points.length - 1].x} ${chartHeight - paddingY} L ${points[0].x} ${chartHeight - paddingY} Z`
    : '';

  const TYPE_COLORS = ['#059669', '#10B981', '#0D9488', '#0284C7', '#D97706', '#8B5CF6'];

  return (
    <div style={{ paddingBottom: '3rem' }}>
      {/* Header Bar */}
      <div className="header-bar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 className="page-title" style={{ fontSize: '1.75rem', margin: 0, color: 'var(--text-main)' }}>Executive Intelligence Overview</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.25rem' }}>
            Real-time document ingestion velocity, spend analytics, and automated classification health.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={fetchDashboardData} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
          <RefreshCw size={15} />
          Refresh Live Data
        </button>
      </div>

      {/* KPI Cards Grid */}
      {kpis && (
        <div className="grid-kpis" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
          
          {/* Card 1: Total Volume */}
          <div className="card" style={{ background: '#ffffff', border: '1px solid #d1fae5' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span className="kpi-title" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '600' }}>Total Processed</span>
              <FileText size={20} style={{ color: 'var(--primary)' }} />
            </div>
            <div className="kpi-val" style={{ fontSize: '2.1rem', fontWeight: '800', color: 'var(--text-dark)' }}>
              {kpis.volume.total_processed.toLocaleString()}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: '#047857', marginTop: '0.4rem', fontWeight: '600' }}>
              <CheckCircle size={14} />
              <span>{kpis.volume.auto_accepted} Auto-Accepted ({kpis.classification_health.auto_accept_rate}%)</span>
            </div>
          </div>

          {/* Card 2: Auto-Accept Rate */}
          <div className="card" style={{ background: '#ffffff', border: '1px solid #d1fae5' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span className="kpi-title" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '600' }}>Auto-Accept Accuracy</span>
              <TrendingUp size={20} style={{ color: 'var(--primary)' }} />
            </div>
            <div className="kpi-val" style={{ fontSize: '2.1rem', fontWeight: '800', color: 'var(--primary)' }}>
              {kpis.classification_health.auto_accept_rate}%
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
              <Layers size={14} />
              <span>{kpis.volume.llm_fallback} LLM Disambiguations</span>
            </div>
          </div>

          {/* Card 3: Open Risks */}
          <div className="card" style={{ background: '#ffffff', border: '1px solid #ffe4e6' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span className="kpi-title" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '600' }}>Active High/Critical Risks</span>
              <ShieldAlert size={20} style={{ color: 'var(--accent-rose)' }} />
            </div>
            <div className="kpi-val" style={{ fontSize: '2.1rem', fontWeight: '800', color: 'var(--accent-rose)' }}>
              {kpis.risk_summary.critical + kpis.risk_summary.high}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
              <AlertTriangle size={14} style={{ color: '#d97706' }} />
              <span>Med: {kpis.risk_summary.medium} | Low: {kpis.risk_summary.low}</span>
            </div>
          </div>

          {/* Card 4: Processing Performance */}
          <div className="card" style={{ background: '#ffffff', border: '1px solid #d1fae5' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span className="kpi-title" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '600' }}>Avg Processing Latency</span>
              <Clock size={20} style={{ color: 'var(--primary)' }} />
            </div>
            <div className="kpi-val" style={{ fontSize: '2.1rem', fontWeight: '800', color: 'var(--primary)' }}>
              {kpis.processing_performance.avg_processing_time_sec}s
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
              <Calendar size={14} />
              <span>Today's Ingestion: {kpis.processing_performance.total_volume_today} docs</span>
            </div>
          </div>

        </div>
      )}

      {/* Main Interactive Telemetry Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Left Interactive Graph Card */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: '700', color: 'var(--text-main)' }}>Document Ingestion Analytics</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', margin: 0 }}>Visualizing datewise trends and distribution breakdown</p>
            </div>
            
            {/* Metric Toggle Tabs */}
            <div style={{ display: 'flex', background: '#f1f5f9', padding: '0.2rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
              <button 
                onClick={() => setActiveTab('datewise')}
                style={{ 
                  padding: '0.35rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '600', cursor: 'pointer', border: 'none',
                  background: activeTab === 'datewise' ? 'var(--primary)' : 'transparent',
                  color: activeTab === 'datewise' ? '#ffffff' : '#64748b'
                }}
              >
                Datewise Timeline
              </button>
              <button 
                onClick={() => setActiveTab('spend')}
                style={{ 
                  padding: '0.35rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '600', cursor: 'pointer', border: 'none',
                  background: activeTab === 'spend' ? 'var(--primary)' : 'transparent',
                  color: activeTab === 'spend' ? '#ffffff' : '#64748b'
                }}
              >
                Spend by Vendor
              </button>
              <button 
                onClick={() => setActiveTab('types')}
                style={{ 
                  padding: '0.35rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '600', cursor: 'pointer', border: 'none',
                  background: activeTab === 'types' ? 'var(--primary)' : 'transparent',
                  color: activeTab === 'types' ? '#ffffff' : '#64748b'
                }}
              >
                Doc Types
              </button>
            </div>
          </div>

          {/* TAB 1: Datewise Area Line Graph */}
          {activeTab === 'datewise' && (
            <div style={{ position: 'relative', width: '100%', overflowX: 'auto' }}>
              <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
                <defs>
                  <linearGradient id="leafyGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10B981" stopOpacity="0.35" />
                    <stop offset="100%" stopColor="#10B981" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Horizontal Grid lines */}
                {[0, 0.33, 0.66, 1].map((ratio, i) => {
                  const y = paddingY + ratio * (chartHeight - paddingY * 2);
                  return (
                    <line key={i} x1={paddingX} y1={y} x2={chartWidth - paddingX} y2={y} stroke="#e2e8f0" strokeDasharray="3 3" opacity="0.7" />
                  );
                })}

                {/* Filled Gradient Area */}
                <path d={areaPathD} fill="url(#leafyGradient)" />

                {/* Smooth Curve Line */}
                <path d={linePathD} fill="none" stroke="#059669" strokeWidth="3" strokeLinecap="round" />

                {/* Interactive Points */}
                {points.map((pt, idx) => (
                  <g key={idx} onMouseEnter={() => setHoveredPoint(pt)} onMouseLeave={() => setHoveredPoint(null)}>
                    <circle cx={pt.x} cy={pt.y} r="5" fill="#ffffff" stroke="#059669" strokeWidth="3" style={{ cursor: 'pointer' }} />
                    <text x={pt.x} y={chartHeight - 4} textAnchor="middle" fill="#64748b" fontSize="10" fontWeight="500">
                      {pt.label}
                    </text>
                  </g>
                ))}
              </svg>

              {/* Hover Tooltip */}
              {hoveredPoint && (
                <div style={{
                  position: 'absolute', top: `${(hoveredPoint.y / chartHeight) * 100}%`, left: `${(hoveredPoint.x / chartWidth) * 100}%`,
                  transform: 'translate(-50%, -120%)', background: '#064E3B', border: '1px solid #10B981', padding: '0.4rem 0.75rem',
                  borderRadius: '6px', color: '#fff', fontSize: '0.8rem', pointerEvents: 'none', boxShadow: '0 4px 12px rgba(6,78,59,0.2)'
                }}>
                  <div style={{ fontWeight: '600', color: '#A7F3D0' }}>{hoveredPoint.label}</div>
                  <div>Volume: {hoveredPoint.value} docs</div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Spend by Vendor Horizontal Bar Chart */}
          {activeTab === 'spend' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem', minHeight: '190px', justifyContent: 'center' }}>
              {spendData.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', fontSize: '0.9rem' }}>No vendor spend telemetry recorded yet.</p>
              ) : (
                spendData.map((item, idx) => {
                  const pct = Math.min((item.value / maxSpendVal) * 100, 100);
                  return (
                    <div key={idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
                        <span style={{ fontWeight: '600', color: '#0f172a' }}>{item.label}</span>
                        <span style={{ fontWeight: '700', color: 'var(--primary)' }}>${item.value.toLocaleString()}</span>
                      </div>
                      <div style={{ width: '100%', height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
                        <div 
                          style={{ 
                            width: `${pct}%`, height: '100%', borderRadius: '4px',
                            background: 'linear-gradient(90deg, #059669 0%, #34D399 100%)',
                            transition: 'width 0.6s ease-out'
                          }} 
                        />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* TAB 3: Document Type Breakdown */}
          {activeTab === 'types' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem', minHeight: '190px', justifyContent: 'center' }}>
              {typeData.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', fontSize: '0.9rem' }}>No classified document types recorded yet.</p>
              ) : (
                typeData.map((item, idx) => {
                  const pct = Math.round((item.value / totalDocsCount) * 100);
                  const color = TYPE_COLORS[idx % TYPE_COLORS.length];
                  return (
                    <div key={idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
                        <span style={{ fontWeight: '600', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <span style={{ width: '9px', height: '9px', borderRadius: '50%', background: color }} />
                          {item.label}
                        </span>
                        <span style={{ fontWeight: '600', color: '#64748b' }}>{item.value} docs ({pct}%)</span>
                      </div>
                      <div style={{ width: '100%', height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
                        <div 
                          style={{ 
                            width: `${pct}%`, height: '100%', borderRadius: '4px', background: color,
                            transition: 'width 0.6s ease-out'
                          }} 
                        />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}

        </div>

        {/* Right Side: Decision Breakdown & Pipeline Health Card */}
        <div className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', background: '#ffffff' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: '700', color: 'var(--text-main)', marginBottom: '0.25rem' }}>Classification Health</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '1.25rem' }}>Ensemble & Disambiguation Routing</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {decisionData.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No classification decisions generated yet.</p>
              ) : (
                decisionData.map((item, idx) => {
                  let badgeBg = '#ecfdf5';
                  let badgeColor = '#047857';
                  if (item.label === 'HUMAN_REVIEW') {
                    badgeBg = '#fef3c7';
                    badgeColor = '#b45309';
                  } else if (item.label === 'REVIEW_LLM_FALLBACK') {
                    badgeBg = '#ffe4e6';
                    badgeColor = '#be123c';
                  }

                  return (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <div>
                        <span style={{ 
                          fontSize: '0.75rem', fontWeight: '700', padding: '0.25rem 0.6rem', borderRadius: '6px',
                          background: badgeBg, color: badgeColor, textTransform: 'uppercase'
                        }}>
                          {item.label.replace('_', ' ')}
                        </span>
                      </div>
                      <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#0f172a' }}>{item.value}</span>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          <div style={{ marginTop: '1.5rem', padding: '0.85rem 1rem', background: '#f0fdf4', borderRadius: '8px', border: '1px solid #a7f3d0' }}>
            <div style={{ fontSize: '0.82rem', fontWeight: '700', color: '#047857', marginBottom: '0.2rem' }}>
              🌿 Ensemble Pipeline Active
            </div>
            <div style={{ fontSize: '0.78rem', color: '#064e3b' }}>
              Parallel LightGBM + XGBoost soft-voting ensemble with Gemini 2.5 Flash LLM Disambiguation judge.
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
