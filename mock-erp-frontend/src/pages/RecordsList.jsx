import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function RecordsList() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  const fetchRecords = async () => {
    try {
      const res = await api.get('/erp/records');
      setRecords(res.data.items);
    } catch (err) {
      console.error(err);
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
      alert('Seeding failed (ensure admin role token is set)');
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

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2>ERP Master Ledgers & Transactions</h2>
        <button onClick={handleSeedData} className="btn-erp btn-pay" disabled={seeding}>
          {seeding ? 'Seeding DB...' : 'Seed Mock ERP Baseline Data'}
        </button>
      </div>

      <div className="card-erp">
        {loading ? (
          <p>Loading ERP records...</p>
        ) : (
          <table className="table-erp">
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Type</th>
                <th>Party Name</th>
                <th>Amount</th>
                <th>Source</th>
                <th>ERP Workflow Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map((rec) => (
                <tr key={rec.id}>
                  <td style={{ fontFamily: 'monospace' }}>{rec.id.slice(0, 8)}...</td>
                  <td>{rec.record_type}</td>
                  <td><strong>{rec.party_name}</strong></td>
                  <td>${rec.amount ? rec.amount.toLocaleString() : '0.00'}</td>
                  <td>
                    <span className={`badge-erp ${rec.source === 'seed' ? 'badge-seed' : 'badge-pipeline'}`}>
                      {rec.source === 'seed' ? 'Mock Seed Data' : 'Pipeline-Generated'}
                    </span>
                  </td>
                  <td>
                    <strong style={{ textTransform: 'uppercase', fontSize: '0.8rem' }}>{rec.erp_status}</strong>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.4rem' }}>
                      {rec.erp_status === 'draft' && (
                        <button onClick={() => handleStatusTransition(rec.id, 'pending_approval')} className="btn-erp btn-pay" style={{ fontSize: '0.75rem' }}>
                          Submit
                        </button>
                      )}
                      {rec.erp_status === 'pending_approval' && (
                        <button onClick={() => handleStatusTransition(rec.id, 'approved')} className="btn-erp btn-approve" style={{ fontSize: '0.75rem' }}>
                          Approve
                        </button>
                      )}
                      {rec.erp_status === 'approved' && (
                        <button onClick={() => handleStatusTransition(rec.id, 'paid')} className="btn-erp btn-approve" style={{ fontSize: '0.75rem' }}>
                          Mark Paid
                        </button>
                      )}
                      {rec.erp_status !== 'rejected' && rec.erp_status !== 'paid' && (
                        <button onClick={() => handleStatusTransition(rec.id, 'rejected')} className="btn-erp btn-reject" style={{ fontSize: '0.75rem' }}>
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
    </div>
  );
}
