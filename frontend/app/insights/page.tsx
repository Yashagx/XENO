'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Insight } from '@/lib/types';
import { TrendingUp, Lightbulb, Target, BookOpen, BarChart2, Zap, ArrowUp, ArrowDown } from 'lucide-react';
import { timeAgo, formatPct, formatCurrency } from '@/lib/utils';

/* ─── Mini Sparkline (pure SVG, no deps) ─────────────────────── */
function Sparkline({ data, color = '#6366f1', height = 40 }: { data: number[]; color?: string; height?: number }) {
  if (!data || data.length < 2) return null;
  const max = Math.max(...data, 1);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 200;
  const h = height;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / range) * (h - 4) - 2;
    return `${x},${y}`;
  });
  const polyline = pts.join(' ');
  // Area fill
  const areaPath = `M0,${h} L${pts[0]} ${pts.map(p => `L${p}`).join(' ')} L${w},${h} Z`;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: '100%', height }} preserveAspectRatio="none">
      <defs>
        <linearGradient id={`sg-${color.replace('#','')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill={`url(#sg-${color.replace('#','')})`} />
      <polyline points={polyline} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}

/* ─── Bar Chart (pure SVG) ──────────────────────────────────── */
function BarChart({ data, color = '#6366f1', height = 60 }: { data: number[]; color?: string; height?: number }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data, 1);
  const w = 200;
  const barW = w / data.length - 2;
  return (
    <svg viewBox={`0 0 ${w} ${height}`} style={{ width: '100%', height }} preserveAspectRatio="none">
      {data.map((v, i) => {
        const barH = (v / max) * (height - 4);
        const x = i * (w / data.length) + 1;
        const y = height - barH - 2;
        return (
          <rect key={i} x={x} y={y} width={barW} height={barH}
            fill={color} opacity={0.6 + (v / max) * 0.4} rx="2" />
        );
      })}
    </svg>
  );
}

/* ─── Donut Chart (pure SVG) ──────────────────────────────────── */
function DonutChart({ data }: { data: Record<string, number> }) {
  const COLORS: Record<string, string> = { email: '#6366f1', whatsapp: '#10b981', sms: '#f59e0b', rcs: '#3b82f6' };
  const total = Object.values(data).reduce((a, b) => a + b, 0) || 1;
  let offset = 0;
  const slices = Object.entries(data).map(([key, val]) => {
    const pct = val / total;
    const slice = { key, val, pct, offset, color: COLORS[key] || '#8b5cf6' };
    offset += pct;
    return slice;
  });
  const r = 30; const cx = 40; const cy = 40;
  const circum = 2 * Math.PI * r;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <svg viewBox="0 0 80 80" style={{ width: 80, height: 80 }}>
        {slices.map(s => (
          <circle key={s.key} cx={cx} cy={cy} r={r}
            fill="none" stroke={s.color} strokeWidth="12"
            strokeDasharray={`${s.pct * circum} ${circum}`}
            strokeDashoffset={-s.offset * circum}
            transform="rotate(-90 40 40)" />
        ))}
        <circle cx={cx} cy={cy} r={r - 8} fill="var(--bg-card)" />
      </svg>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {slices.map(s => (
          <div key={s.key} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: s.color, flexShrink: 0 }} />
            <span style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{s.key}</span>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-primary)', marginLeft: 'auto' }}>{Math.round(s.pct * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Stat chip ──────────────────────────────────────────────── */
function StatChip({ label, value, sub, color = '#6366f1', up }: { label: string; value: string; sub?: string; color?: string; up?: boolean }) {
  return (
    <div style={{ background: `${color}10`, border: `1px solid ${color}25`, borderRadius: 12, padding: '10px 14px', minWidth: 90 }}>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 800, color, lineHeight: 1 }}>{value}</div>
      {sub && (
        <div style={{ fontSize: 10, color: up === true ? '#10b981' : up === false ? '#ef4444' : 'var(--text-muted)', marginTop: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
          {up === true && <ArrowUp size={9} />}{up === false && <ArrowDown size={9} />}{sub}
        </div>
      )}
    </div>
  );
}

/* ─── Impact badge ───────────────────────────────────────────── */
function ImpactBadge({ impact }: { impact: string }) {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    high:   { bg: '#10b98115', text: '#059669', label: '🔥 High Impact' },
    medium: { bg: '#f59e0b15', text: '#d97706', label: '⚡ Medium Impact' },
    low:    { bg: '#6366f115', text: '#4f46e5', label: '💡 Low Impact' },
  };
  const s = map[impact] || map.low;
  return (
    <span style={{ fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 9999, background: s.bg, color: s.text }}>
      {s.label}
    </span>
  );
}

/* ─── Main Page ──────────────────────────────────────────────── */
export default function LearningConsole() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [selected, setSelected] = useState<Insight | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listInsights()
      .then((d: any) => {
        const ins = d.insights || [];
        setInsights(ins);
        if (ins.length > 0) setSelected(ins[0]);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const totalRevenue = insights.reduce((s, i) => s + ((i.content as any)?.actual_stats?.revenue_inr || 0), 0);
  const avgRoi = insights.length ? (insights.reduce((s, i) => s + ((i.content as any)?.actual_stats?.roi || 0), 0) / insights.length) : 0;
  const avgOpen = insights.length ? (insights.reduce((s, i) => s + ((i.content as any)?.actual_stats?.open_rate || 0), 0) / insights.length) : 0;

  return (
    <div style={{ minHeight: '100vh', padding: '24px', maxWidth: 1200, margin: '0 auto' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <div style={{ width: 40, height: 40, borderRadius: 12, background: 'linear-gradient(135deg,#10b981,#059669)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 12px #10b98140' }}>
          <TrendingUp size={20} color="white" />
        </div>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>Learning Console</h1>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '2px 0 0' }}>AI-generated intelligence from every completed campaign</p>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '80px 0' }}>
          <div style={{ width: 32, height: 32, border: '3px solid #10b98140', borderTopColor: '#10b981', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
        </div>
      ) : insights.length === 0 ? (
        <div className="xeno-card" style={{ textAlign: 'center', padding: '80px 40px' }}>
          <BookOpen size={40} color="var(--text-muted)" style={{ margin: '0 auto 12px' }} />
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, margin: 0 }}>No insights yet</p>
          <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>Complete a campaign to see AI learning here.</p>
        </div>
      ) : (
        <>
          {/* Portfolio KPIs */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
            <div className="xeno-card" style={{ background: 'linear-gradient(135deg,#6366f108,#6366f115)', borderColor: '#6366f130', padding: 16 }}>
              <div style={{ fontSize: 10, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Total Campaigns Analysed</div>
              <div style={{ fontSize: 32, fontWeight: 900, color: '#6366f1', lineHeight: 1 }}>{insights.length}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>across {new Set(insights.map(i => (i.content as any)?.channel)).size} channels</div>
            </div>
            <div className="xeno-card" style={{ background: 'linear-gradient(135deg,#10b98108,#10b98115)', borderColor: '#10b98130', padding: 16 }}>
              <div style={{ fontSize: 10, color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Total Revenue Generated</div>
              <div style={{ fontSize: 28, fontWeight: 900, color: '#10b981', lineHeight: 1 }}>{formatCurrency(totalRevenue)}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>from AI-orchestrated campaigns</div>
            </div>
            <div className="xeno-card" style={{ background: 'linear-gradient(135deg,#f59e0b08,#f59e0b15)', borderColor: '#f59e0b30', padding: 16 }}>
              <div style={{ fontSize: 10, color: '#f59e0b', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Average ROI</div>
              <div style={{ fontSize: 32, fontWeight: 900, color: '#f59e0b', lineHeight: 1 }}>{avgRoi.toFixed(1)}x</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>vs 1.8x industry benchmark</div>
            </div>
            <div className="xeno-card" style={{ background: 'linear-gradient(135deg,#8b5cf608,#8b5cf615)', borderColor: '#8b5cf630', padding: 16 }}>
              <div style={{ fontSize: 10, color: '#8b5cf6', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Avg Open Rate</div>
              <div style={{ fontSize: 32, fontWeight: 900, color: '#8b5cf6', lineHeight: 1 }}>{formatPct(avgOpen)}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>vs 22% industry benchmark</div>
            </div>
          </div>

          {/* Main 3-column layout */}
          <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 16 }}>

            {/* Sidebar — campaign list */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6, fontWeight: 600 }}>
                CAMPAIGNS ({insights.length})
              </div>
              {insights.map(ins => {
                const actual = (ins.content as any)?.actual_stats || {};
                const isSelected = selected?.id === ins.id;
                return (
                  <button
                    key={ins.id}
                    onClick={() => setSelected(ins)}
                    style={{
                      width: '100%', textAlign: 'left', padding: '12px 14px',
                      background: isSelected ? 'linear-gradient(135deg,#6366f110,#6366f118)' : 'var(--bg-card)',
                      border: isSelected ? '1.5px solid #6366f140' : '1px solid var(--border)',
                      borderRadius: 12, cursor: 'pointer', transition: 'all 0.15s',
                      boxShadow: isSelected ? '0 2px 12px #6366f118' : 'none',
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4, lineHeight: 1.3 }}>
                      {ins.campaign_name || (ins.content as any)?.campaign_name || 'Campaign'}
                    </div>

                    {/* Mini metrics */}
                    <div style={{ display: 'flex', gap: 10, marginTop: 6 }}>
                      {actual.open_rate > 0 && (
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 9, color: 'var(--text-muted)' }}>Open</div>
                          <div style={{ fontSize: 12, fontWeight: 800, color: '#6366f1' }}>{formatPct(actual.open_rate)}</div>
                        </div>
                      )}
                      {actual.click_rate > 0 && (
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 9, color: 'var(--text-muted)' }}>Click</div>
                          <div style={{ fontSize: 12, fontWeight: 800, color: '#10b981' }}>{formatPct(actual.click_rate)}</div>
                        </div>
                      )}
                      {actual.roi > 0 && (
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 9, color: 'var(--text-muted)' }}>ROI</div>
                          <div style={{ fontSize: 12, fontWeight: 800, color: '#f59e0b' }}>{actual.roi}x</div>
                        </div>
                      )}
                    </div>

                    {/* Trend sparkline */}
                    {(ins.content as any)?.trend_data?.hourly_opens && (
                      <div style={{ marginTop: 8, opacity: 0.8 }}>
                        <Sparkline data={(ins.content as any).trend_data.hourly_opens.slice(6, 22)} color={isSelected ? '#6366f1' : '#94a3b8'} height={28} />
                      </div>
                    )}

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 6 }}>
                      <ImpactBadge impact={(ins.content as any)?.impact || 'medium'} />
                      <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>{timeAgo(ins.generated_at)}</span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Detail panel */}
            {selected ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {/* Executive Summary */}
                <div className="xeno-card" style={{ background: 'linear-gradient(135deg,#6366f108,#8b5cf608)', borderColor: '#6366f125', padding: 20 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                    <div style={{ width: 28, height: 28, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <TrendingUp size={14} color="white" />
                    </div>
                    <span style={{ fontSize: 11, fontWeight: 700, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Executive Summary</span>
                    <ImpactBadge impact={selected.content?.impact || 'medium'} />
                  </div>
                  <p style={{ fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.7, margin: 0, fontWeight: 500 }}>
                    {selected.content?.executive_summary}
                  </p>
                </div>

                {/* Stats Row */}
                {selected.content?.actual_stats && (
                  <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                    <StatChip label="Open Rate"   value={formatPct(selected.content.actual_stats.open_rate || 0)}       color="#6366f1" up={true}  sub={selected.content.vs_simulation?.open_rate_variance} />
                    <StatChip label="Click Rate"  value={formatPct(selected.content.actual_stats.click_rate || 0)}      color="#10b981" up={true} />
                    <StatChip label="Conversion"  value={formatPct(selected.content.actual_stats.conversion_rate || 0)} color="#f59e0b" up={true} />
                    <StatChip label="ROI"         value={`${selected.content.actual_stats.roi}x`}                       color="#8b5cf6" up={true}  sub={selected.content.vs_simulation?.roi_variance} />
                    <StatChip label="Revenue"     value={formatCurrency(selected.content.actual_stats.revenue_inr || 0)} color="#06b6d4" />
                    <StatChip label="Total Sent"  value={(selected.content.actual_stats.total_sent || 0).toLocaleString()} color="#64748b" />
                  </div>
                )}

                {/* Charts Row */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                  {/* Hourly Opens Chart */}
                  {selected.content?.trend_data?.hourly_opens && (
                    <div className="xeno-card" style={{ padding: 16 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                        <BarChart2 size={14} color="#6366f1" />
                        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Hourly Opens (24h)</span>
                      </div>
                      <Sparkline data={selected.content.trend_data.hourly_opens} color="#6366f1" height={60} />
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
                        <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>12AM</span>
                        <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>12PM</span>
                        <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>11PM</span>
                      </div>
                    </div>
                  )}

                  {/* Daily Conversion Chart */}
                  {selected.content?.trend_data?.daily_conversions && (
                    <div className="xeno-card" style={{ padding: 16 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                        <Zap size={14} color="#10b981" />
                        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Daily Conversions (7d)</span>
                      </div>
                      <BarChart data={selected.content.trend_data.daily_conversions} color="#10b981" height={60} />
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
                        {['D1','D2','D3','D4','D5','D6','D7'].map(d => (
                          <span key={d} style={{ fontSize: 9, color: 'var(--text-muted)' }}>{d}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Channel split + Simulation vs Actual */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                  {/* Channel split */}
                  {selected.content?.trend_data?.channel_split && (
                    <div className="xeno-card" style={{ padding: 16 }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>Channel Mix</div>
                      <DonutChart data={selected.content.trend_data.channel_split} />
                    </div>
                  )}

                  {/* Simulation vs Actual */}
                  {selected.content?.vs_simulation && (
                    <div className="xeno-card" style={{ padding: 16, background: 'linear-gradient(135deg,#10b98106,#10b98112)', borderColor: '#10b98125' }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: '#059669', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>AI Prediction Accuracy</div>
                      {Object.entries(selected.content.vs_simulation).map(([k, v]) => (
                        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px solid #10b98115' }}>
                          <span style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{k.replace(/_/g,' ')}</span>
                          <span style={{ fontSize: 12, fontWeight: 800, color: '#10b981' }}>+{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Key Insights + Recommendations */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                  {(selected.content?.key_insights?.length ?? 0) > 0 && (
                    <div className="xeno-card" style={{ padding: 16 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                        <Lightbulb size={14} color="#f59e0b" />
                        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Key Insights</span>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {selected.content.key_insights.map((insight: string, i: number) => (
                          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, padding: '8px 10px', background: '#f59e0b0a', borderRadius: 8, border: '1px solid #f59e0b18' }}>
                            <span style={{ color: '#f59e0b', fontWeight: 900, fontSize: 11, flexShrink: 0, marginTop: 1 }}>{i + 1}</span>
                            <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>{insight}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {(selected.content?.next_campaign_recommendations?.length ?? 0) > 0 && (
                    <div className="xeno-card" style={{ padding: 16 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                        <Target size={14} color="#10b981" />
                        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Recommendations</span>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {selected.content.next_campaign_recommendations.map((rec: string, i: number) => (
                          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, padding: '8px 10px', background: '#10b9810a', borderRadius: 8, border: '1px solid #10b98118' }}>
                            <span style={{ color: '#10b981', fontWeight: 900, fontSize: 13, flexShrink: 0 }}>✓</span>
                            <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>{rec}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Win / Improve */}
                {(selected.content?.winning_element || selected.content?.improvement_area) && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                    {selected.content?.winning_element && (
                      <div className="xeno-card" style={{ padding: 14, background: '#10b9810a', borderColor: '#10b98125' }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: '#10b981', textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.06em' }}>🏆 What Worked</div>
                        <p style={{ fontSize: 13, color: 'var(--text-primary)', margin: 0, fontWeight: 600, lineHeight: 1.4 }}>{selected.content.winning_element}</p>
                      </div>
                    )}
                    {selected.content?.improvement_area && (
                      <div className="xeno-card" style={{ padding: 14, background: '#ef44440a', borderColor: '#ef444425' }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: '#ef4444', textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.06em' }}>📈 Improve Next</div>
                        <p style={{ fontSize: 13, color: 'var(--text-primary)', margin: 0, fontWeight: 600, lineHeight: 1.4 }}>{selected.content.improvement_area}</p>
                      </div>
                    )}
                  </div>
                )}

              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
                Select a campaign from the left to view its insight
              </div>
            )}
          </div>
        </>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
