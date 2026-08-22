import React, { useEffect, useState, useRef } from 'react';
import { Send, Bot, User, FileText, Loader2 } from 'lucide-react';
import api from '../services/api';

export default function Chatbot() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    async function initSession() {
      try {
        const res = await api.post('/chat/sessions', { title: 'RAG ERP Chat Session' });
        setSessionId(res.data.session_id);
      } catch (err) {
        console.error("Session init error:", err);
      }
    }
    initSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userText = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userText }]);
    setSending(true);

    try {
      let activeSession = sessionId;
      if (!activeSession) {
        const sRes = await api.post('/chat/sessions', { title: 'RAG ERP Chat Session' });
        activeSession = sRes.data.session_id;
        setSessionId(activeSession);
      }

      const res = await api.post(`/chat/sessions/${activeSession}/messages`, { content: userText });
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: res.data.content,
        source_document_ids: res.data.source_document_ids
      }]);
    } catch (err) {
      console.error("RAG chat error:", err);
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'Apologies, failed to process query against document repository.'
      }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 4.5rem)' }}>
      <div className="header-bar">
        <div>
          <h1 className="page-title">RAG Document Assistant</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.15rem' }}>
            Hybrid vector & keyword semantic search across all ingested business documents
          </p>
        </div>
      </div>

      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: '1.25rem', background: '#ffffff', borderRadius: '14px', border: '1px solid #D1FAE5' }}>
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#64748B', marginTop: '4rem', padding: '2rem' }}>
              <div style={{ background: '#ECFDF5', width: '56px', height: '56px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem auto', color: '#059669' }}>
                <Bot size={28} />
              </div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#064E3B', marginBottom: '0.5rem' }}>Ask natural-language questions about your documents</h3>
              <p style={{ fontSize: '0.88rem', color: '#64748B', maxWidth: '450px', margin: '0 auto' }}>
                e.g., "What are the total amounts on Acme Corp invoices?", "Which POs are pending approval?", or "Summarize CRM leads."
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '78%',
                  background: msg.role === 'user' ? '#059669' : '#F4F7F4',
                  color: msg.role === 'user' ? '#ffffff' : '#064E3B',
                  padding: '0.9rem 1.15rem',
                  borderRadius: msg.role === 'user' ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                  border: msg.role === 'user' ? 'none' : '1px solid #D1FAE5',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
                  lineHeight: '1.5'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.35rem', fontSize: '0.78rem', fontWeight: '600', opacity: 0.9 }}>
                  {msg.role === 'user' ? <User size={13} /> : <Bot size={13} />}
                  <span>{msg.role === 'user' ? 'You' : 'IntelliParse RAG AI'}</span>
                </div>
                <div style={{ fontSize: '0.92rem' }}>{msg.content}</div>

                {msg.source_document_ids && msg.source_document_ids.length > 0 && (
                  <div style={{ marginTop: '0.6rem', paddingTop: '0.5rem', borderTop: msg.role === 'user' ? '1px solid rgba(255,255,255,0.2)' : '1px solid #D1FAE5', fontSize: '0.75rem', display: 'flex', gap: '0.4rem', flexWrap: 'wrap', alignItems: 'center' }}>
                    <span style={{ opacity: 0.8, fontWeight: '500' }}>Sources:</span>
                    {msg.source_document_ids.map((docId) => (
                      <span key={docId} style={{ background: msg.role === 'user' ? 'rgba(255,255,255,0.2)' : '#ECFDF5', color: msg.role === 'user' ? '#fff' : '#047857', padding: '0.15rem 0.45rem', borderRadius: '4px', border: msg.role === 'user' ? 'none' : '1px solid #A7F3D0' }}>
                        <FileText size={10} style={{ display: 'inline', marginRight: '3px' }} />
                        {docId.slice(0, 8)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
          {sending && (
            <div style={{ alignSelf: 'flex-start', background: '#F4F7F4', color: '#059669', padding: '0.75rem 1rem', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', border: '1px solid #D1FAE5' }}>
              <Loader2 size={16} className="animate-spin" />
              <span>Analyzing document repository & generating reasoning...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '0.6rem', marginTop: '1rem' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question across all uploaded invoices, POs, and leads..."
            disabled={sending}
            style={{
              flex: 1,
              padding: '0.8rem 1.1rem',
              background: '#F8FAFC',
              border: '1px solid #CBD5E1',
              color: '#0F172A',
              borderRadius: '10px',
              fontSize: '0.92rem',
              outline: 'none'
            }}
          />
          <button type="submit" className="btn btn-primary" disabled={sending || !input.trim()} style={{ background: '#059669', color: '#fff', border: 'none', borderRadius: '10px', padding: '0.8rem 1.4rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: sending || !input.trim() ? 'not-allowed' : 'pointer', opacity: sending || !input.trim() ? 0.6 : 1 }}>
            <Send size={16} />
            <span>{sending ? 'Searching...' : 'Send'}</span>
          </button>
        </form>
      </div>
    </div>
  );
}
