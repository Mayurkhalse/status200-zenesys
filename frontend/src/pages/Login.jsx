import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Login() {
  const [email, setEmail] = useState('admin@intelliparse.ai');
  const [password, setPassword] = useState('Admin@123');
  const [isRegister, setIsRegister] = useState(false);
  const [fullName, setFullName] = useState('Admin User');
  const [role, setRole] = useState('analyst');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await api.post('/auth/register', { email, password, full_name: fullName, role });
      }
      const res = await api.post('/auth/login', { email, password });
      localStorage.setItem('token', res.data.access_token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Authentication failed');
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-main)' }}>
      <div className="card" style={{ width: '420px', padding: '2.5rem', boxShadow: '0 10px 25px rgba(6, 78, 59, 0.08)', border: '1px solid #d1fae5' }}>
        <h2 style={{ marginBottom: '0.25rem', textAlign: 'center', color: 'var(--text-main)', fontSize: '1.75rem', fontWeight: '800' }}>IntelliParse</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: '1.75rem', fontSize: '0.88rem' }}>
          Document Intelligence Platform for ERP Systems
        </p>
        
        {error && <div style={{ color: 'var(--accent-rose)', marginBottom: '1rem', fontSize: '0.85rem', padding: '0.5rem', background: '#ffe4e6', borderRadius: '6px', textAlign: 'center', fontWeight: '600' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', fontWeight: '600', color: '#334155' }}>Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '6px' }}
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', fontWeight: '600', color: '#334155' }}>Account Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '6px' }}
                >
                  <option value="analyst">Analyst (Upload & Own Documents)</option>
                  <option value="viewer">Viewer (Read-Only Access)</option>
                  <option value="admin">Administrator (System-Wide Access)</option>
                </select>
              </div>
            </>
          )}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', fontWeight: '600', color: '#334155' }}>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '6px' }}
            />
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', fontWeight: '600', color: '#334155' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%', padding: '0.65rem 0.85rem', borderRadius: '6px' }}
            />
          </div>
          <button type="submit" className="btn" style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}>
            {isRegister ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        <div style={{ marginTop: '1.25rem', textAlign: 'center', fontSize: '0.85rem' }}>
          <button
            onClick={() => setIsRegister(!isRegister)}
            style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontWeight: '600' }}
          >
            {isRegister ? 'Already have an account? Sign In' : 'Need an account? Register'}
          </button>
        </div>
      </div>
    </div>
  );
}
