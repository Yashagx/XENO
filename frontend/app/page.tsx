'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Campaign } from '@/lib/types';
import { IntentInput } from '@/components/oracle/IntentInput';
import { AgentTimeline } from '@/components/oracle/AgentTimeline';
import { useEventStream } from '@/hooks/useEventStream';
import { timeAgo, formatPct, formatCurrency } from '@/lib/utils';
import { Zap, ArrowRight, Activity, Users, Target, TrendingUp, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import Link from 'next/link';

const AGENT_STEPS = [
  { n: 1, id: 'intent_parser',      label: 'Intent Parser',   desc: 'Extracts goals, audience, and constraints from natural language' },
  { n: 2, id: 'memory_agent',       label: 'Memory Agent',    desc: 'Retrieves past campaign learnings and customer history' },
  { n: 3, id: 'segmentation_agent', label: 'Segmentation',    desc: 'Clusters customers using RFM + twin embeddings' },
  { n: 4, id: 'persona_agent',      label: 'Persona Agent',   desc: 'Creates 2-3 archetypal customer personas for the segment' },
  { n: 5, id: 'strategy_agent',     label: 'Strategy',        desc: 'Picks channels, timing, budget allocation, and messaging tone' },
  { n: 6, id: 'copywriter_agent',   label: 'Copywriter',      desc: 'Generates personalised copy per persona per channel with A/B variants' },
  { n: 7, id: 'simulator_agent',    label: 'Simulator',       desc: 'Monte Carlo simulation predicting open rate, ROI, revenue' },
  { n: 8, id: 'execution_agent',    label: 'Execution',       desc: 'Dispatches messages via channel service with idempotency keys' },
  { n: 9, id: 'learning_agent',     label: 'Learning',        desc: 'Reconciles predicted vs actual stats and updates twin models' },
  { n: 10, id: 'insight_agent',     label: 'Insight',         desc: 'Distils campaign learnings into persistent memory for future runs' },
];

function HowItWorks() {
  const [open, setOpen] = useState(false);
  return (
    <div className="xeno-card">
      <button
        onClick={() => setOpen(!open)}
        style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', padding: 0 }}
      >
        <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">How It Works — 10 AI Agents</span>
        {open ? <ChevronUp className="w-3.5 h-3.5 text-[var(--text-muted)]" /> : <ChevronDown className="w-3.5 h-3.5 text-[var(--text-muted)]" />}
      </button>
      {open && (
        <div style={{ marginTop: '14px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {AGENT_STEPS.map(s => (
            <div key={s.n} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
              <span style={{
                flexShrink: 0, width: '20px', height: '20px', borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                color: 'white', fontSize: '10px', fontWeight: 700,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>{s.n}</span>
              <div>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>{s.label}</span>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '6px' }}>{s.desc}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}



export default function OracleCommandCenter() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [activeCampaign, setActiveCampaign] = useState<Campaign | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const { events, connected } = useEventStream(activeCampaign?.id);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 6000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [camData, custStats] = await Promise.all([
        api.listCampaigns({ limit: 6 }) as Promise<any>,
        api.getCustomerStats() as Promise<any>,
      ]);
      setCampaigns(camData.campaigns || []);
      setStats(custStats);
    } catch {}
  }

  async function handleIntent(intent: string) {
    setIsCreating(true);
    try {
      const result = await api.createCampaign({ intent }) as any;
      setActiveCampaign({ id: result.campaign_id, intent, name: 'Campaign in progress...', status: 'segmenting' } as Campaign);
      loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsCreating(false);
    }
  }

  useEffect(() => {
    if (!activeCampaign) return;
    const t = setInterval(async () => {
      try {
        const c = await api.getCampaign(activeCampaign.id) as Campaign;
        setActiveCampaign(c);
        if (['ready', 'completed', 'failed'].includes(c.status)) loadData();
      } catch {}
    }, 3000);
    return () => clearInterval(t);
  }, [activeCampaign?.id]);

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center">
            <Zap className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[var(--text-primary)]">Oracle Command Center</h1>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">Express your marketing goal — AI agents handle the rest</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-[var(--border)] shadow-sm">
          <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-500 animate-pulse' : 'bg-gray-300'}`} />
          <span className="text-xs text-[var(--text-secondary)]">{connected ? 'Live' : 'Connecting...'}</span>
        </div>
      </div>

      {/* Stat cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Customers', value: (stats.total_customers || 0).toLocaleString(), icon: Users, bg: 'bg-indigo-50', iconColor: 'text-indigo-500' },
            { label: 'Active Campaigns', value: campaigns.filter(c => !['completed','failed','draft'].includes(c.status)).length, icon: Activity, bg: 'bg-sky-50', iconColor: 'text-sky-500' },
            { label: 'High Churn Risk', value: (stats.high_churn_count || 0).toLocaleString(), icon: TrendingUp, bg: 'bg-rose-50', iconColor: 'text-rose-500' },
            { label: 'Avg Customer LTV', value: `₹${((stats.avg_total_spend || 0) / 1000).toFixed(1)}K`, icon: Target, bg: 'bg-emerald-50', iconColor: 'text-emerald-600' },
          ].map(({ label, value, icon: Icon, bg, iconColor }) => (
            <div key={label} className="xeno-card">
              <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center mb-3`}>
                <Icon className={`w-4 h-4 ${iconColor}`} />
              </div>
              <div className="text-2xl font-bold text-[var(--text-primary)]">{value}</div>
              <div className="text-xs text-[var(--text-muted)] mt-1">{label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Left: Intent input + pipeline */}
        <div className="space-y-5">
          <div className="xeno-card">
            <div className="text-xs font-semibold text-[var(--text-muted)] mb-4 uppercase tracking-wider">New Campaign Intent</div>
            <IntentInput onSubmit={handleIntent} isLoading={isCreating} />
          </div>

          {/* How it works */}
          <HowItWorks />


          {activeCampaign && (
            <div className="xeno-card-highlight animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="text-sm font-semibold text-[var(--text-primary)]">Agent Pipeline</div>
                  <div className="text-xs text-[var(--text-muted)] mt-0.5 line-clamp-1">{activeCampaign.intent}</div>
                </div>
                <span className={`status-badge status-${activeCampaign.status}`}>{activeCampaign.status}</span>
              </div>
              <AgentTimeline events={events} campaignStatus={activeCampaign.status} />

              {activeCampaign.status === 'ready' && (
                <div className="mt-4 p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="text-sm font-semibold text-emerald-700 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" /> Campaign Ready
                      </div>
                      <div className="text-xs text-emerald-600 mt-0.5">Review predictions before launching</div>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <Link href={`/campaigns/${activeCampaign.id}`}>
                        <button className="text-sm px-3 py-1.5 rounded-lg bg-white border border-[var(--border)] text-[var(--text-primary)] hover:bg-[var(--bg-muted)] transition-all">
                          Review
                        </button>
                      </Link>
                      <button
                        onClick={async () => {
                          await api.approveCampaign(activeCampaign.id);
                          setActiveCampaign(p => p ? { ...p, status: 'executing' } : null);
                        }}
                        className="btn-primary text-sm px-4 py-1.5"
                      >
                        Launch 🚀
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Recent campaigns */}
        <div className="space-y-3">
          <div className="flex items-center justify-between mb-1">
            <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Recent Campaigns</div>
            <Link href="/campaigns" className="text-xs text-indigo-500 hover:text-indigo-700 flex items-center gap-1">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {campaigns.length === 0 ? (
            <div className="xeno-card text-center py-16">
              <div className="text-4xl mb-3">🎯</div>
              <p className="text-sm text-[var(--text-secondary)]">No campaigns yet.</p>
              <p className="text-xs text-[var(--text-muted)] mt-1">Express your first marketing intent above.</p>
            </div>
          ) : (
            campaigns.map(c => (
              <Link key={c.id} href={`/campaigns/${c.id}`}>
                <div className="xeno-card cursor-pointer hover:shadow-md transition-all group mb-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-[var(--text-primary)] group-hover:text-indigo-600 transition-colors truncate">
                        {c.name}
                      </div>
                      <div className="text-xs text-[var(--text-muted)] mt-0.5 line-clamp-1">{c.intent}</div>
                    </div>
                    <div className="flex flex-col items-end gap-1.5 shrink-0">
                      <span className={`status-badge status-${c.status}`}>{c.status}</span>
                      <span className="text-[10px] text-[var(--text-muted)]">{timeAgo(c.created_at)}</span>
                    </div>
                  </div>
                  {c.simulation_result && Object.keys(c.simulation_result).length > 0 && (
                    <div className="flex gap-5 mt-3 pt-3 border-t border-[var(--border)]">
                      {[
                        { label: 'Open', val: formatPct(c.simulation_result.open_rate?.p50 || 0) },
                        { label: 'Click', val: formatPct(c.simulation_result.click_rate?.p50 || 0) },
                        { label: 'Revenue', val: formatCurrency(c.simulation_result.revenue_inr?.p50 || 0) },
                        { label: 'ROI', val: `${c.simulation_result.roi?.toFixed(1)}x` },
                      ].map(m => (
                        <div key={m.label}>
                          <div className="text-[10px] text-[var(--text-muted)]">{m.label}</div>
                          <div className="text-xs font-semibold text-[var(--text-primary)]">{m.val}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
