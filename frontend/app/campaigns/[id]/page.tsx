'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Download, ChevronDown, ChevronUp, CheckCircle } from 'lucide-react';
import { timeAgo, formatPct, formatCurrency, getChannelIcon, getAgentIcon } from '@/lib/utils';

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, { bg: string; color: string; border: string }> = {
    draft:       { bg: '#f8fafc', color: '#64748b', border: '#e2e8f0' },
    segmenting:  { bg: '#eef2ff', color: '#6366f1', border: '#c7d2fe' },
    strategizing:{ bg: '#faf5ff', color: '#a855f7', border: '#e9d5ff' },
    writing:     { bg: '#fffbeb', color: '#d97706', border: '#fde68a' },
    simulating:  { bg: '#f0f9ff', color: '#0ea5e9', border: '#bae6fd' },
    ready:       { bg: '#ecfdf5', color: '#059669', border: '#a7f3d0' },
    executing:   { bg: '#fffbeb', color: '#d97706', border: '#fde68a' },
    completed:   { bg: '#ecfdf5', color: '#059669', border: '#a7f3d0' },
    failed:      { bg: '#fff1f2', color: '#e11d48', border: '#fecdd3' },
  };
  const s = colors[status] || colors.draft;
  return (
    <span style={{
      padding: '3px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 700,
      textTransform: 'uppercase', letterSpacing: '0.06em',
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
    }}>
      {status}
    </span>
  );
}

function GaugeChart({ value, max, label, color }: { value: number; max: number; label: string; color: string }) {
  const pct = Math.min(100, (value / max) * 100);
  const r = 38;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <div style={{ textAlign: 'center' }}>
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="var(--bg-muted, #f3f4f6)" strokeWidth="8" />
        <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{ transition: 'stroke-dasharray 1s ease' }}
        />
        <text x="50" y="54" textAnchor="middle" fontSize="14" fontWeight="700" fill="var(--text-primary, #1a1d2e)">
          {label}
        </text>
      </svg>
    </div>
  );
}

export default function CampaignDetailPage() {
  const { id } = useParams() as { id: string };
  const [campaign, setCampaign] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [traceOpen, setTraceOpen] = useState<Record<number, boolean>>({});
  const [activePersona, setActivePersona] = useState(0);
  const [exporting, setExporting] = useState(false);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    loadCampaign();
    const interval = setInterval(loadCampaign, 5000);
    return () => clearInterval(interval);
  }, [id]);

  async function loadCampaign() {
    try {
      const [c, s] = await Promise.all([
        api.getCampaign(id) as Promise<any>,
        api.getCampaignStats(id) as Promise<any>,
      ]);
      setCampaign(c);
      setStats(s);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function handleExport() {
    setExporting(true);
    try {
      const result = await api.exportCampaign(id) as any;
      if (result.s3_url) {
        window.open(result.s3_url, '_blank');
      } else {
        alert('Export unavailable — AWS S3 not configured.');
      }
    } catch {
      alert('Export failed.');
    } finally {
      setExporting(false);
    }
  }

  async function handleApprove() {
    setApproving(true);
    try {
      await api.approveCampaign(id);
      await loadCampaign();
    } catch {}
    finally { setApproving(false); }
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div style={{ textAlign: 'center' }}>
        <div style={{ width: '32px', height: '32px', border: '3px solid var(--border)', borderTopColor: 'var(--accent)', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 12px' }} />
        <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Loading campaign...</p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  if (!campaign) return (
    <div className="min-h-screen flex items-center justify-center">
      <div style={{ textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)', marginBottom: '8px' }}>Campaign not found.</p>
        <Link href="/campaigns" style={{ color: 'var(--accent)', fontSize: '14px' }}>← Back to campaigns</Link>
      </div>
    </div>
  );

  const sim = campaign.simulation_result || {};
  const personas = campaign.personas || [];
  const copies = campaign.copies || [];
  const trace = campaign.agent_trace || [];
  const strategy = campaign.strategy || {};
  const explanation = campaign.explanation || {};
  const actual = campaign.actual_stats || {};
  const isReady = campaign.status === 'ready';
  const isCompleted = campaign.status === 'completed';

  const agentNames: Record<string, string> = {
    intent_parser: 'Intent Parser', memory_agent: 'Memory Agent', segmentation_agent: 'Segmentation',
    persona_agent: 'Persona Agent', strategy_agent: 'Strategy', copywriter_agent: 'Copywriter',
    simulator_agent: 'Simulator', execution_agent: 'Execution', learning_agent: 'Learning', insight_agent: 'Insight',
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '1.5rem' }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      {/* Back nav */}
      <Link href="/campaigns" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '13px', marginBottom: '1.25rem', textDecoration: 'none' }}>
        <ArrowLeft size={14} /> Back to Campaigns
      </Link>

      {/* ─── Section 1: Header ─── */}
      <div className="xeno-card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', flexWrap: 'wrap' }}>
              <h1 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>{campaign.name}</h1>
              <StatusBadge status={campaign.status} />
            </div>
            <div style={{ padding: '10px 14px', background: 'var(--accent-light)', border: '1.5px solid #c7d2fe', borderRadius: '8px', fontSize: '13px', color: 'var(--accent)', fontStyle: 'italic' }}>
              "{campaign.intent}"
            </div>
            <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
              Created {timeAgo(campaign.created_at)}
              {campaign.segment?.customer_count && (
                <span style={{ marginLeft: '12px' }}>· <strong style={{ color: 'var(--text-secondary)' }}>{campaign.segment.customer_count.toLocaleString()}</strong> customers in segment</span>
              )}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexShrink: 0, flexWrap: 'wrap' }}>
            {isReady && (
              <button
                onClick={handleApprove}
                disabled={approving}
                className="btn-primary"
                style={{ fontSize: '12px', padding: '8px 14px' }}
              >
                <CheckCircle size={13} />
                {approving ? 'Launching…' : 'Approve & Launch'}
              </button>
            )}
            {isCompleted && (
              <button
                onClick={handleExport}
                disabled={exporting}
                className="btn-primary"
                style={{ fontSize: '12px', padding: '8px 14px' }}
              >
                <Download size={13} />
                {exporting ? 'Exporting...' : 'Export to S3'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ─── Section 2: Simulation Metrics ─── */}
      {Object.keys(sim).length > 0 && (
        <div className="xeno-card" style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1rem' }}>
            Simulation Results
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: sim.summary ? '1rem' : 0 }}>
            <GaugeChart
              value={(sim.open_rate?.p50 || sim.predicted_open_rate || 0) * 100}
              max={100}
              label={formatPct(sim.open_rate?.p50 || sim.predicted_open_rate || 0)}
              color="#6366f1"
            />
            <GaugeChart
              value={(sim.click_rate?.p50 || sim.predicted_click_rate || 0) * 100}
              max={100}
              label={formatPct(sim.click_rate?.p50 || sim.predicted_click_rate || 0)}
              color="#059669"
            />
            <GaugeChart
              value={(sim.conversion_rate?.p50 || sim.predicted_conversion_rate || 0) * 100}
              max={100}
              label={formatPct(sim.conversion_rate?.p50 || sim.predicted_conversion_rate || 0)}
              color="#d97706"
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0' }}>
            {['Open Rate', 'Click Rate', 'Conv. Rate'].map(l => (
              <div key={l} style={{ textAlign: 'center', fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{l}</div>
            ))}
          </div>
          {sim.roi_estimate && (
            <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <div style={{ flex: 1, padding: '12px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>Projected ROI</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#059669' }}>{sim.roi_estimate?.toFixed ? sim.roi_estimate.toFixed(1) + 'x' : sim.roi_estimate}</div>
              </div>
              {sim.estimated_revenue && (
                <div style={{ flex: 1, padding: '12px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>Est. Revenue</div>
                  <div style={{ fontSize: '20px', fontWeight: 800, color: '#6366f1' }}>{formatCurrency(sim.estimated_revenue)}</div>
                </div>
              )}
              {sim.confidence_score != null && (
                <div style={{ flex: 1, padding: '12px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>Confidence</div>
                  <div style={{ fontSize: '20px', fontWeight: 800, color: '#6366f1' }}>{Math.round(sim.confidence_score * 100)}%</div>
                </div>
              )}
            </div>
          )}
          {sim.summary && (
            <div style={{ marginTop: '1rem', padding: '12px 14px', background: '#eef0fe', border: '1px solid #c7d2fe', borderRadius: '8px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {sim.summary}
            </div>
          )}
          {sim.risk_factors?.length > 0 && (
            <div style={{ marginTop: '10px', padding: '12px 14px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: '#d97706', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '6px' }}>⚠ Risk Factors</div>
              <ul style={{ margin: 0, padding: '0 0 0 16px' }}>
                {sim.risk_factors.map((r: string, i: number) => (
                  <li key={i} style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '2px' }}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* ─── Section 3: Actual Stats (post-execution) ─── */}
      {isCompleted && Object.keys(actual).length > 0 && (
        <div className="xeno-card" style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1rem' }}>
            Actual Performance
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
            {[
              { label: 'Sent', value: actual.sent?.toLocaleString() || '—', color: '#6366f1' },
              { label: 'Opened', value: actual.opened?.toLocaleString() || '—', color: '#059669' },
              { label: 'Clicked', value: actual.clicked?.toLocaleString() || '—', color: '#d97706' },
              { label: 'Converted', value: actual.converted?.toLocaleString() || '—', color: '#e11d48' },
            ].map(m => (
              <div key={m.label} style={{ padding: '12px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>{m.label}</div>
                <div style={{ fontSize: '18px', fontWeight: 800, color: m.color }}>{m.value}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Section 4: Personas ─── */}
      {personas.length > 0 && (
        <div className="xeno-card" style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1rem' }}>
            Customer Personas
          </div>
          {/* Tabs */}
          <div style={{ display: 'flex', gap: '4px', marginBottom: '1rem', flexWrap: 'wrap' }}>
            {personas.map((p: any, i: number) => (
              <button
                key={i}
                onClick={() => setActivePersona(i)}
                style={{
                  padding: '5px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: 600,
                  border: 'none', cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.15s',
                  background: activePersona === i ? '#6366f1' : 'var(--bg-surface)',
                  color: activePersona === i ? 'white' : 'var(--text-secondary)',
                  boxShadow: activePersona === i ? '0 2px 8px rgba(99,102,241,0.3)' : '0 1px 3px rgba(0,0,0,0.05)',
                  border: activePersona === i ? 'none' : '1px solid var(--border)',
                } as React.CSSProperties}
              >
                {p.name || `Persona ${i + 1}`}
              </button>
            ))}
          </div>
          {/* Persona detail */}
          {personas[activePersona] && (() => {
            const p = personas[activePersona];
            return (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  {p.description && <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '12px' }}>{p.description}</p>}
                  {p.pain_points?.length > 0 && (
                    <div style={{ marginBottom: '10px' }}>
                      <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '6px' }}>Pain Points</div>
                      {p.pain_points.map((pt: string, j: number) => (
                        <div key={j} style={{ display: 'flex', gap: '6px', marginBottom: '4px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                          <span style={{ color: '#e11d48', flexShrink: 0 }}>•</span> {pt}
                        </div>
                      ))}
                    </div>
                  )}
                  {p.motivations?.length > 0 && (
                    <div>
                      <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '6px' }}>Motivations</div>
                      {p.motivations.map((m: string, j: number) => (
                        <div key={j} style={{ display: 'flex', gap: '6px', marginBottom: '4px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                          <span style={{ color: '#059669', flexShrink: 0 }}>✓</span> {m}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div>
                  {p.preferred_channels?.length > 0 && (
                    <div style={{ marginBottom: '10px' }}>
                      <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '6px' }}>Preferred Channels</div>
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        {p.preferred_channels.map((ch: string) => (
                          <span key={ch} style={{ padding: '3px 10px', background: '#eef0fe', color: '#6366f1', borderRadius: '9999px', fontSize: '12px', fontWeight: 600 }}>
                            {getChannelIcon(ch)} {ch}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {p.size && (
                    <div style={{ padding: '10px 14px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '13px' }}>
                      <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Segment size: </span>
                      <strong style={{ color: 'var(--text-primary)' }}>{p.size.toLocaleString()}</strong>
                    </div>
                  )}
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* ─── Section 5: Generated Copy ─── */}
      {copies.length > 0 && (
        <div className="xeno-card" style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1rem' }}>
            Generated Copy
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {copies.map((copy: any, i: number) => (
              <div key={i} style={{ padding: '14px', borderRadius: '10px', background: 'var(--bg-surface)', border: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap' }}>
                  <span style={{
                    fontSize: '11px', fontWeight: 700, padding: '2px 10px', borderRadius: '9999px',
                    background: '#eef0fe', color: '#6366f1', border: '1px solid #c7d2fe',
                    textTransform: 'uppercase', letterSpacing: '0.06em',
                  }}>
                    {getChannelIcon(copy.channel)} {copy.channel}
                  </span>
                  {copy.variant && (
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>Variant {copy.variant}</span>
                  )}
                  {copy.tone && (
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>· {copy.tone}</span>
                  )}
                </div>
                {copy.subject && (
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>Subject: {copy.subject}</div>
                )}
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-line', margin: 0 }}>{copy.body}</p>
                {copy.cta && (
                  <div style={{ marginTop: '10px' }}>
                    <span style={{ display: 'inline-block', padding: '6px 16px', background: '#6366f1', color: 'white', borderRadius: '6px', fontSize: '12px', fontWeight: 700 }}>
                      {copy.cta}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Section 6: Strategy ─── */}
      {Object.keys(strategy).length > 0 && (
        <div className="xeno-card" style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1rem' }}>
            Campaign Strategy
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {strategy.rationale && (
              <div style={{ padding: '12px 14px', background: '#eef0fe', border: '1px solid #c7d2fe', borderRadius: '8px' }}>
                <div style={{ fontSize: '10px', fontWeight: 700, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '6px' }}>Rationale</div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>{strategy.rationale}</p>
              </div>
            )}
            {strategy.channel_allocation && (
              <div>
                <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>Channel Allocation</div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {Object.entries(strategy.channel_allocation).map(([ch, pct]: any) => (
                    <div key={ch} style={{ padding: '8px 14px', borderRadius: '8px', background: 'var(--bg-surface)', border: '1px solid var(--border)', textAlign: 'center', minWidth: '80px' }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>{getChannelIcon(ch)} {ch}</div>
                      <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--accent)' }}>{Math.round(pct * 100)}%</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {strategy.send_time_recommendation && (
              <div style={{ padding: '12px 14px', background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: '8px' }}>
                <div style={{ fontSize: '10px', fontWeight: 700, color: '#059669', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '4px' }}>⏰ Send Time</div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>{strategy.send_time_recommendation}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── Section 7: Agent Trace ─── */}
      {trace.length > 0 && (
        <div className="xeno-card" style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1rem' }}>
            Agent Reasoning Trace
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {trace.map((step: any, i: number) => {
              const isOpen = !!traceOpen[i];
              const agentName = agentNames[step.agent_id] || step.agent_id;
              const confidence = step.confidence ?? step.confidence_score;
              return (
                <div key={i} style={{ border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden' }}>
                  <button
                    onClick={() => setTraceOpen(prev => ({ ...prev, [i]: !prev[i] }))}
                    style={{
                      width: '100%', display: 'flex', alignItems: 'center', gap: '10px',
                      padding: '10px 14px', background: 'var(--bg-surface)', border: 'none',
                      cursor: 'pointer', fontFamily: 'inherit', textAlign: 'left',
                    }}
                  >
                    <span style={{ fontSize: '16px', flexShrink: 0 }}>{getAgentIcon(step.agent_id)}</span>
                    <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', flex: 1 }}>{agentName}</span>
                    {confidence != null && (
                      <span style={{ fontSize: '11px', color: confidence >= 0.7 ? '#059669' : confidence >= 0.5 ? '#d97706' : '#e11d48', fontWeight: 700 }}>
                        {Math.round(confidence * 100)}%
                      </span>
                    )}
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', flexShrink: 0 }}>
                      {step.duration_ms != null ? `${step.duration_ms}ms` : ''}
                    </span>
                    {isOpen ? <ChevronUp size={14} color="var(--text-muted)" /> : <ChevronDown size={14} color="var(--text-muted)" />}
                  </button>
                  {isOpen && (
                    <div style={{ padding: '12px 14px', background: 'var(--bg-base)', borderTop: '1px solid var(--border)', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      {step.output_summary || step.output || step.reasoning || 'No detail available.'}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ─── Oracle Explanation ─── */}
      {explanation.why && (
        <div className="xeno-card" style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '12px' }}>
            Oracle Explanation
          </div>
          {explanation.why && (
            <div style={{ marginBottom: '10px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '4px' }}>Why This Campaign</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>{explanation.why}</p>
            </div>
          )}
          {explanation.what_if_wrong && (
            <div style={{ padding: '10px 14px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px', marginTop: '10px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: '#d97706', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '4px' }}>What If Wrong</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>{explanation.what_if_wrong}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
