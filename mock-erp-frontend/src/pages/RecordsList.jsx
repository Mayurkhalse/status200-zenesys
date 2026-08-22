import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { 
  Home, FileText, ShoppingCart, TrendingUp, Users, Package, 
  Settings, Search, Plus, Filter, ExternalLink, RefreshCw, Layers
} from 'lucide-react';

export default function RecordsList({ globalSearch = '', setGlobalSearch }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [activeModule, setActiveModule] = useState('Home');
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchRecords = async () => {
    try {
      const res = await api.get('/erp/records?limit=100');
      setRecords(res.data.items || []);
    } catch (err) {
      console.error('Failed to load ERP master records:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleSeedData = async () => {
    setSeeding(true);
    try {
      await api.post('/erp/seed', { count_per_type: 3 });
      fetchRecords();
    } catch (err) {
      alert('Seeding completed or DB updated');
      fetchRecords();
    } finally {
      setSeeding(false);
    }
  };

  const handleStatusTransition = async (id, newStatus) => {
    try {
      await api.patch(`/erp/records/${id}/status`, { new_status: newStatus });
      fetchRecords();
    } catch (err) {
      alert('Status update failed');
    }
  };

  // Filter records based on Active Sidebar Module, Search Query, and Status Filter
  const filteredRecords = records.filter(rec => {
    // Module type filter
    if (activeModule === 'Accounting' && !['BUSINESS_INVOICE', 'RECEIPT', 'PAYMENT_RECEIPT'].includes(rec.record_type)) return false;
    if (activeModule === 'Buying' && !['PURCHASE_ORDER', 'RFQ'].includes(rec.record_type)) return false;
    if (activeModule === 'Selling' && !['SALES_ORDER', 'QUOTATION'].includes(rec.record_type)) return false;
    if (activeModule === 'CRM' && !['LEAD', 'PROPOSAL'].includes(rec.record_type)) return false;
    if (activeModule === 'Operations' && !['CONTRACT', 'DELIVERY_NOTE', 'CREDIT_NOTE', 'DEBIT_NOTE'].includes(rec.record_type)) return false;

    // Global Search query filter across all fields
    if (globalSearch) {
      const q = globalSearch.toLowerCase();
      const matchParty = rec.party_name ? rec.party_name.toLowerCase().includes(q) : false;
      const matchType = rec.record_type ? rec.record_type.toLowerCase().includes(q) : false;
      const matchId = rec.id ? rec.id.toLowerCase().includes(q) : false;
      const matchStatus = rec.erp_status ? rec.erp_status.toLowerCase().includes(q) : false;
      const matchSource = rec.source ? rec.source.toLowerCase().includes(q) : false;
      if (!matchParty && !matchType && !matchId && !matchStatus && !matchSource) return false;
    }

    // Status filter
    if (statusFilter !== 'all' && rec.erp_status !== statusFilter) return false;

    return true;
  });

  // Calculate Module Category Counts for Shortcuts Header Bar
  const invoiceCount = records.filter(r => r.record_type === 'BUSINESS_INVOICE').length;
  const poCount = records.filter(r => r.record_type === 'PURCHASE_ORDER').length;
  const salesCount = records.filter(r => r.record_type === 'SALES_ORDER').length;
  const leadCount = records.filter(r => r.record_type === 'LEAD').length;
  const quoteCount = records.filter(r => r.record_type === 'QUOTATION').length;
  const contractCount = records.filter(r => r.record_type === 'CONTRACT').length;

  // Income vs Expense Chart Stats calculation
  const totalIncome = records.filter(r => ['BUSINESS_INVOICE', 'SALES_ORDER'].includes(r.record_type)).reduce((acc, r) => acc + (r.amount || 0), 0);
  const totalExpense = records.filter(r => ['PURCHASE_ORDER', 'RFQ'].includes(r.record_type)).reduce((acc, r) => acc + (r.amount || 0), 0);
  const maxFinancialVal = Math.max(totalIncome, totalExpense, 1);

  return (
    <div className="erp-container">
      {/* Left Sidebar Navigation (ERPNext Style) */}
      <aside className="erp-sidebar">
        <div>
          <div className="erp-sidebar-section-title">PUBLIC</div>
          <div className={`erp-nav-item ${activeModule === 'Home' ? 'active' : ''}`} onClick={() => setActiveModule('Home')}>
            <Home size={17} />
            <span>Home</span>
          </div>
          <div className={`erp-nav-item ${activeModule === 'Accounting' ? 'active' : ''}`} onClick={() => setActiveModule('Accounting')}>
            <FileText size={17} />
            <span>Accounting</span>
          </div>
          <div className={`erp-nav-item ${activeModule === 'Buying' ? 'active' : ''}`} onClick={() => setActiveModule('Buying')}>
            <ShoppingCart size={17} />
            <span>Buying</span>
          </div>
          <div className={`erp-nav-item ${activeModule === 'Selling' ? 'active' : ''}`} onClick={() => setActiveModule('Selling')}>
            <TrendingUp size={17} />
            <span>Selling</span>
          </div>
          <div className={`erp-nav-item ${activeModule === 'CRM' ? 'active' : ''}`} onClick={() => setActiveModule('CRM')}>
            <Users size={17} />
            <span>CRM</span>
          </div>
          <div className={`erp-nav-item ${activeModule === 'Operations' ? 'active' : ''}`} onClick={() => setActiveModule('Operations')}>
            <Package size={17} />
            <span>Assets & Stock</span>
          </div>
        </div>

        <div style={{ marginTop: 'auto' }}>
          <div className="erp-sidebar-section-title">SETTINGS</div>
          <div className="erp-nav-item">
            <Settings size={17} />
            <span>ERPNext Settings</span>
          </div>
        </div>
      </aside>

      {/* Main Workspace Area */}
      <main className="erp-main-content">
        {/* Module Title & Top Toolbar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: '700' }}>
              {activeModule === 'Home' ? 'Workspace Overview' : `${activeModule} Module`}
            </h1>
            <p style={{ color: 'var(--erp-text-muted)', fontSize: '0.85rem', marginTop: '0.15rem' }}>
              Master ledger transactions and automated document pipeline records
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button onClick={handleSeedData} className="btn-erp-action btn-erp-primary" disabled={seeding} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Plus size={15} />
              <span>{seeding ? 'Seeding DB...' : 'Seed Baseline ERP Data'}</span>
            </button>
          </div>
        </div>

        {/* Shortcuts Bar (Matching User's Screenshot) */}
        <div className="erp-card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
          <div style={{ fontSize: '0.88rem', fontWeight: '600', marginBottom: '0.75rem', color: '#475569' }}>
            Your Shortcuts & Category Counts
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div className="shortcut-pill" onClick={() => setActiveModule('Accounting')}>
              <span>Sales Invoice</span>
              <span className="shortcut-badge">{invoiceCount}</span>
            </div>
            <div className="shortcut-pill" onClick={() => setActiveModule('Buying')}>
              <span>Purchase Order</span>
              <span className="shortcut-badge">{poCount}</span>
            </div>
            <div className="shortcut-pill" onClick={() => setActiveModule('Selling')}>
              <span>Quotations</span>
              <span className="shortcut-badge">{quoteCount}</span>
            </div>
            <div className="shortcut-pill" onClick={() => setActiveModule('CRM')}>
              <span>CRM Leads</span>
              <span className="shortcut-badge">{leadCount}</span>
            </div>
            <div className="shortcut-pill" onClick={() => setActiveModule('Operations')}>
              <span>Contracts & Agreements</span>
              <span className="shortcut-badge">{contractCount}</span>
            </div>
          </div>
        </div>

        {/* P&L Financial Graph (Matching Screenshot) */}
        {activeModule === 'Home' && (
          <div className="erp-card" style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <span style={{ fontWeight: '600', fontSize: '0.95rem' }}>P&L Master Summary (Income vs Expense)</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--erp-text-muted)' }}>FY 2026-2027</span>
            </div>
            <div style={{ display: 'flex', gap: '2rem', height: '140px', alignItems: 'flex-end', paddingBottom: '0.5rem', borderBottom: '1px solid var(--erp-border)' }}>
              {/* Income Bar */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                <div style={{ 
                  width: '60%', 
                  height: `${(totalIncome / maxFinancialVal) * 100}%`, 
                  background: 'var(--erp-pink)', 
                  borderRadius: '4px 4px 0 0',
                  minHeight: '20px',
                  transition: 'height 0.5s ease'
                }} />
                <span style={{ fontSize: '0.8rem', marginTop: '0.4rem', fontWeight: '500' }}>Income (${Math.round(totalIncome).toLocaleString()})</span>
              </div>
              {/* Expense Bar */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                <div style={{ 
                  width: '60%', 
                  height: `${(totalExpense / maxFinancialVal) * 100}%`, 
                  background: 'var(--erp-primary)', 
                  borderRadius: '4px 4px 0 0',
                  minHeight: '20px',
                  transition: 'height 0.5s ease'
                }} />
                <span style={{ fontSize: '0.8rem', marginTop: '0.4rem', fontWeight: '500' }}>Expense (${Math.round(totalExpense).toLocaleString()})</span>
              </div>
            </div>
          </div>
        )}

        {/* Master Records Table Card */}
        <div className="erp-card">
          {/* Table Header Filter Toolbar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#f8fafc', border: '1px solid var(--erp-border)', padding: '0.35rem 0.65rem', borderRadius: '6px', width: '280px' }}>
              <Search size={15} style={{ color: '#94a3b8' }} />
              <input 
                type="text" 
                placeholder="Search party name or record ID..." 
                value={globalSearch}
                onChange={(e) => setGlobalSearch && setGlobalSearch(e.target.value)}
                style={{ border: 'none', background: 'transparent', outline: 'none', width: '100%', fontSize: '0.85rem' }}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Filter size={15} style={{ color: '#64748b' }} />
              <select 
                value={statusFilter} 
                onChange={(e) => setStatusFilter(e.target.value)}
                style={{ border: '1px solid var(--erp-border)', background: '#fff', padding: '0.35rem 0.65rem', borderRadius: '6px', fontSize: '0.85rem', outline: 'none' }}
              >
                <option value="all">All Workflow Statuses</option>
                <option value="draft">Draft</option>
                <option value="pending_approval">Pending Approval</option>
                <option value="approved">Approved</option>
                <option value="paid">Paid</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--erp-text-muted)' }}>
              Loading ERP Master Ledgers...
            </div>
          ) : filteredRecords.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--erp-text-muted)' }}>
              No master records found for <strong>{activeModule}</strong> module.
            </div>
          ) : (
            <table className="erp-table">
              <thead>
                <tr>
                  <th>Record ID</th>
                  <th>Record Type</th>
                  <th>Party Name</th>
                  <th>Amount</th>
                  <th>Source</th>
                  <th>Workflow Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((rec) => (
                  <tr key={rec.id}>
                    <td style={{ fontFamily: 'monospace', fontWeight: '600', color: '#334155' }}>
                      {rec.id.slice(0, 8)}...
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', fontWeight: '600', padding: '0.15rem 0.5rem', background: '#f1f5f9', borderRadius: '4px', color: '#475569' }}>
                        {rec.record_type}
                      </span>
                    </td>
                    <td style={{ fontWeight: '600' }}>{rec.party_name}</td>
                    <td style={{ fontWeight: '600', color: '#0f172a' }}>
                      ${rec.amount ? rec.amount.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '0.00'}
                    </td>
                    <td>
                      <span className={`badge-source ${rec.source === 'seed' ? 'badge-seed-src' : 'badge-pipeline-src'}`}>
                        {rec.source === 'seed' ? 'Mock Seed' : 'Pipeline Auto-Created'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge-status badge-${rec.erp_status}`}>
                        {rec.erp_status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.35rem' }}>
                        {rec.erp_status === 'draft' && (
                          <button onClick={() => handleStatusTransition(rec.id, 'pending_approval')} className="btn-erp-action">
                            Submit
                          </button>
                        )}
                        {rec.erp_status === 'pending_approval' && (
                          <button onClick={() => handleStatusTransition(rec.id, 'approved')} className="btn-erp-action btn-erp-primary">
                            Approve
                          </button>
                        )}
                        {rec.erp_status === 'approved' && (
                          <button onClick={() => handleStatusTransition(rec.id, 'paid')} className="btn-erp-action btn-erp-primary">
                            Mark Paid
                          </button>
                        )}
                        {rec.erp_status !== 'rejected' && rec.erp_status !== 'paid' && (
                          <button onClick={() => handleStatusTransition(rec.id, 'rejected')} className="btn-erp-action" style={{ color: 'var(--erp-danger)' }}>
                            Reject
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
}
