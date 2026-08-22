import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import RecordsList from './pages/RecordsList';
import { Search, Bell, HelpCircle } from 'lucide-react';

export default function App() {
  const [globalSearch, setGlobalSearch] = useState('');
  const searchInputRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'g') {
        e.preventDefault();
        if (searchInputRef.current) {
          searchInputRef.current.focus();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <BrowserRouter>
      {/* ERPNext Top Navigation Header */}
      <header className="erp-navbar">




        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Bell size={18} style={{ color: '#64748b', cursor: 'pointer' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.85rem', color: '#64748b', cursor: 'pointer' }}>
            <HelpCircle size={17} />
            <span>Help</span>
          </div>
          <div className="erp-user-avatar" title="System Administrator">
            RK
          </div>
        </div>
      </header>

      <Routes>
        <Route path="/*" element={<RecordsList globalSearch={globalSearch} setGlobalSearch={setGlobalSearch} />} />
      </Routes>
    </BrowserRouter>
  );
}
