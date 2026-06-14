'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Campaign } from '@/lib/types';
import { timeAgo, formatPct, formatCurrency } from '@/lib/utils';
import { LayoutDashboard, Plus, Search } from 'lucide-react';
import Link from 'next/link';

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    api.listCampaigns({ limit: 100 })
      .then((d: any) => setCampaigns(d.campaigns || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = campaigns.filter(c => {
    const matchSearch = !search || c.name?.toLowerCase().includes(search.toLowerCase()) || c.intent?.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'all' || c.status === filter;
    return matchSearch && matchFilter;
  });

  const statuses = ['all', 'draft', 'segmenting', 'ready', 'executing', 'completed', 'failed'];

  return (
    <div className="min-h-screen p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-100 flex items-center justify-center">
            <LayoutDashboard className="w-4 h-4 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[var(--text-primary)]">Campaigns</h1>
            <p className="text-xs text-[var(--text-muted)]">{campaigns.length} total campaigns</p>
          </div>
        </div>
        <Link href="/">
          <button className="btn-primary text-sm">
            <Plus className="w-4 h-4" /> New Campaign
          </button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Search campaigns..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="xeno-input pl-8 text-xs py-2"
          />
        </div>
        <div className="flex gap-1.5">
          {statuses.map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`text-xs px-3 py-1.5 rounded-full font-medium transition-all capitalize ${
                filter === s
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white border border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Campaign list */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="xeno-card text-center py-20">
          <div className="text-4xl mb-3">📋</div>
          <p className="text-sm text-[var(--text-secondary)]">No campaigns found</p>
          <p className="text-xs text-[var(--text-muted)] mt-1">Create your first campaign from the Oracle Command Center</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(c => {
            const actual = (c as any).actual_stats || {};
            const hasActual = actual.open_rate > 0 || actual.revenue_inr > 0;
            const sim = c.simulation_result || {};
            return (
              <Link key={c.id} href={`/campaigns/${c.id}`}>
                <div className="xeno-card cursor-pointer hover:shadow-md transition-all group mb-3">
                  <div className="flex items-start gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-sm font-semibold text-[var(--text-primary)] group-hover:text-indigo-600 transition-colors truncate">
                          {c.name}
                        </span>
                        <span className={`status-badge status-${c.status} shrink-0`}>{c.status}</span>
                        {hasActual && (
                          <span style={{ fontSize: 9, padding: '2px 6px', borderRadius: 9999, background: '#10b98115', color: '#059669', fontWeight: 700, flexShrink: 0 }}>
                            ✓ ACTUAL
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[var(--text-muted)] line-clamp-1">{c.intent}</p>
                      {/* Inline metrics bar */}
                      {hasActual && (
                        <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
                          {[
                            { label: 'Open', val: formatPct(actual.open_rate), color: '#6366f1' },
                            { label: 'Click', val: formatPct(actual.click_rate), color: '#10b981' },
                            { label: 'Conv', val: formatPct(actual.conversion_rate), color: '#f59e0b' },
                          ].map(m => (
                            <div key={m.label} style={{ textAlign: 'center' }}>
                              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{m.label}</div>
                              <div style={{ fontSize: 13, fontWeight: 800, color: m.color }}>{m.val}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="text-right shrink-0" style={{ minWidth: 120 }}>
                      <div className="text-[11px] text-[var(--text-muted)]">{timeAgo(c.created_at)}</div>
                      {hasActual ? (
                        <div style={{ marginTop: 6 }}>
                          <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Revenue</div>
                          <div style={{ fontSize: 15, fontWeight: 900, color: '#10b981' }}>{formatCurrency(actual.revenue_inr || 0)}</div>
                          <div style={{ fontSize: 11, fontWeight: 700, color: '#f59e0b', marginTop: 2 }}>{actual.roi}x ROI</div>
                        </div>
                      ) : sim && Object.keys(sim).length > 0 ? (
                        <div className="flex gap-4 mt-2 justify-end">
                          <div className="text-center">
                            <div className="text-[10px] text-[var(--text-muted)]">Pred. Open</div>
                            <div className="text-xs font-semibold text-[var(--text-primary)]">{formatPct(sim.open_rate?.p50 || sim.predicted_open_rate || 0)}</div>
                          </div>
                          <div className="text-center">
                            <div className="text-[10px] text-[var(--text-muted)]">Pred. ROI</div>
                            <div className="text-xs font-semibold text-indigo-500">{sim.roi?.toFixed(1)}x</div>
                          </div>
                        </div>
                      ) : null}
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
