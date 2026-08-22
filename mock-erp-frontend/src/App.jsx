import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import RecordsList from './pages/RecordsList';

export default function App() {
  return (
    <BrowserRouter>
      <div className="navbar-erp">
        <h1 style={{ fontSize: '1.25rem' }}>Enterprise ERP System (Simulated Environment)</h1>
        <span style={{ fontSize: '0.85rem', opacity: 0.8 }}>Shared MongoDB Ledger Active</span>
      </div>
      <Routes>
        <Route path="/" element={<RecordsList />} />
      </Routes>
    </BrowserRouter>
  );
}
