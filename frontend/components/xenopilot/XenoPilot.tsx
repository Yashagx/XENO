'use client';
import { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';
import { X, Send } from 'lucide-react';

const STARTERS = [
  'Who are my top 10 customers?',
  'Which campaign had the best ROI?',
  'How many customers are at churn risk?',
  'Best channel for re-engagement?',
];

interface Message {
  role: 'user' | 'assistant';
  content: string;
  actions?: Array<{ label: string; href: string }>;
  loading?: boolean;
}

export function XenoPilot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage(text: string) {
    if (!text.trim() || loading) return;
    const userMsg: Message = { role: 'user', content: text };
    const history = messages.slice(-8).map(m => ({ role: m.role, content: m.content }));
    setMessages(prev => [...prev, userMsg, { role: 'assistant', content: '', loading: true }]);
    setInput('');
    setLoading(true);
    try {
      const result = await api.xenopilotChat(text, history) as any;
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: 'assistant', content: result.answer, actions: result.suggested_actions }
      ]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: 'assistant', content: `Sorry, I encountered an error: ${err.message}` }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(!open)}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          background: open ? '#4f46e5' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          border: 'none',
          cursor: 'pointer',
          boxShadow: '0 8px 24px rgba(99,102,241,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          transition: 'all 0.2s',
          fontSize: '24px',
        }}
        title="XenoPilot — CRM Intelligence"
      >
        {open ? <X size={22} color="white" /> : <span style={{ color: 'white', fontSize: '20px', lineHeight: 1 }}>✦</span>}
      </button>

      {/* Chat panel */}
      {open && (
        <div style={{
          position: 'fixed',
          bottom: '92px',
          right: '24px',
          width: '400px',
          height: '520px',
          background: 'white',
          borderRadius: '16px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.15), 0 4px 12px rgba(0,0,0,0.08)',
          border: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 999,
          overflow: 'hidden',
          animation: 'slideUp 0.2s ease-out',
        }}>
          {/* Header */}
          <div style={{
            padding: '14px 16px',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}>
            <span style={{ fontSize: '18px' }}>✦</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: '14px', lineHeight: 1.2 }}>XenoPilot</div>
              <div style={{ fontSize: '11px', opacity: 0.8 }}>CRM Intelligence · Live Data</div>
            </div>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {messages.length === 0 && (
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '12px', textAlign: 'center', marginBottom: '12px' }}>
                  Ask me anything about your CRM data
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {STARTERS.map(s => (
                    <button
                      key={s}
                      onClick={() => sendMessage(s)}
                      style={{
                        background: 'var(--bg-muted)',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                        padding: '8px 12px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        color: 'var(--text-secondary)',
                        textAlign: 'left',
                        fontFamily: 'inherit',
                        transition: 'all 0.15s',
                      }}
                      onMouseEnter={e => {
                        (e.currentTarget as HTMLElement).style.borderColor = '#a5b4fc';
                        (e.currentTarget as HTMLElement).style.color = '#6366f1';
                      }}
                      onMouseLeave={e => {
                        (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
                        (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)';
                      }}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{
                  maxWidth: '85%',
                  background: msg.role === 'user' ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : 'var(--bg-muted)',
                  color: msg.role === 'user' ? 'white' : 'var(--text-primary)',
                  borderRadius: msg.role === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                  padding: '10px 12px',
                  fontSize: '13px',
                  lineHeight: 1.5,
                  border: msg.role === 'assistant' ? '1px solid var(--border)' : 'none',
                }}>
                  {msg.loading ? (
                    <div style={{ display: 'flex', gap: '4px', alignItems: 'center', padding: '2px 0' }}>
                      {[0, 1, 2].map(j => (
                        <span key={j} style={{
                          width: '6px', height: '6px', borderRadius: '50%',
                          background: 'var(--text-muted)',
                          animation: `bounce 1.2s ease-in-out ${j * 0.2}s infinite`,
                          display: 'inline-block',
                        }} />
                      ))}
                    </div>
                  ) : msg.content}
                  {msg.actions && msg.actions.length > 0 && (
                    <div style={{ marginTop: '8px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {msg.actions.map(a => (
                        <a
                          key={a.href}
                          href={a.href}
                          style={{
                            display: 'inline-block',
                            padding: '4px 10px',
                            background: 'var(--accent-light)',
                            color: 'var(--accent)',
                            borderRadius: '6px',
                            fontSize: '11px',
                            fontWeight: 600,
                            textDecoration: 'none',
                            border: '1px solid #c7d2fe',
                          }}
                        >
                          {a.label}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div style={{
            padding: '10px 12px',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            gap: '8px',
            alignItems: 'center',
            background: 'white',
          }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); } }}
              placeholder="Ask about customers, campaigns, ROI..."
              disabled={loading}
              style={{
                flex: 1,
                padding: '8px 12px',
                background: 'var(--bg-muted)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                fontSize: '13px',
                fontFamily: 'inherit',
                outline: 'none',
                color: 'var(--text-primary)',
              }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={loading || !input.trim()}
              style={{
                width: '34px', height: '34px', borderRadius: '8px',
                background: input.trim() && !loading ? 'var(--accent)' : 'var(--bg-muted)',
                border: 'none', cursor: input.trim() && !loading ? 'pointer' : 'default',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.15s', flexShrink: 0,
              }}
            >
              <Send size={14} color={input.trim() && !loading ? 'white' : 'var(--text-muted)'} />
            </button>
          </div>
        </div>
      )}

      <style>{`
        @keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); } 40% { transform: scale(1); } }
      `}</style>
    </>
  );
}
