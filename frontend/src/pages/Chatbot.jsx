import React, { useEffect, useState } from 'react';
import { Send, Bot, User, FileText } from 'lucide-react';
import api from '../services/api';

export default function Chatbot() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    async function initSession() {
      try {
        const res = await api.post('/chat/sessions');
        setSessionId(res.data.session_id);
      } catch (err) {
        console.error(err);
      }
    }
    initSession();
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !sessionId || sending) return;

    const userText = input;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userText }]);
    setSending(true);

    try {
      const res = await api.post(`/chat/sessions/${sessionId}/messages`, { content: userText });
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: res.data.content,
        source_document_ids: res.data.source_document_ids
      }]);
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'Apologies, failed to process query against document repository.'
      }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 4rem)' }}>
      <div className="header-bar">
        <h1 className="page-title">RAG Document Chatbot</h1>
      </div>

      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem' }}>
              Ask natural-language questions across all uploaded ERP documents.
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '75%',
                  background: msg.role === 'user' ? 'var(--primary)' : 'var(--bg-card-hover)',
                  padding: '0.85rem 1.1rem',
                  borderRadius: '12px',
                  lineHeight: '1.5'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem', fontSize: '0.8rem', opacity: 0.8 }}>
                  {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                  <span>{msg.role === 'user' ? 'You' : 'IntelliParse AI'}</span>
                </div>
                <div>{msg.content}</div>

                {msg.source_document_ids && msg.source_document_ids.length > 0 && (
                  <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: '0.75rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ opacity: 0.7 }}>Sources:</span>
                    {msg.source_document_ids.map((docId) => (
                      <span key={docId} style={{ background: 'rgba(255,255,255,0.1)', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                        <FileText size={10} style={{ display: 'inline', marginRight: '3px' }} />
                        {docId.slice(0, 8)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g., What are the total amounts on Acme Corp invoices?"
            disabled={sending}
            style={{
              flex: 1,
              padding: '0.75rem 1rem',
              background: '#090d16',
              border: '1px solid var(--border-color)',
              color: '#fff',
              borderRadius: '8px'
            }}
          />
          <button type="submit" className="btn" disabled={sending}>
            <Send size={16} />
            <span>{sending ? 'Searching...' : 'Send'}</span>
          </button>
        </form>
      </div>
    </div>
  );
}
