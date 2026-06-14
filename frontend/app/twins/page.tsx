'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Customer } from '@/lib/types';
import { timeAgo, formatCurrency, formatPct } from '@/lib/utils';
import { Users, Search } from 'lucide-react';
import Link from 'next/link';

export default function TwinExplorer() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('total_spend');
  const [total, setTotal] = useState(0);

  useEffect(() => { loadCustomers(); }, [sortBy]);

  async function loadCustomers() {
    setLoading(true);
    try {
      const d: any = await api.listCustomers({ limit: 50, sort_by: sortBy });
      setCustomers(d.customers || []);
      setTotal(d.total || 0);
    } catch {} finally { setLoading(false); }
  }

  const filtered = search
    ? customers.filter(c => c.name?.toLowerCase().includes(search.toLowerCase()) || c.city?.toLowerCase().includes(search.toLowerCase()))
    : customers;

  const getChurnColor = (p: number) => p > 0.7 ? 'text-rose-600 bg-rose-50' : p > 0.4 ? 'text-amber-600 bg-amber-50' : 'text-emerald-600 bg-emerald-50';

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-violet-100 flex items-center justify-center">
            <Users className="w-4 h-4 text-violet-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[var(--text-primary)]">Twin Explorer</h1>
            <p className="text-xs text-[var(--text-muted)]">{total} digital twins modelled</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Search by name or city..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="xeno-input pl-8 text-xs py-2"
          />
        </div>
        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value)}
          className="xeno-input text-xs py-2 w-44"
        >
          <option value="total_spend">Sort: LTV</option>
          <option value="churn_probability">Sort: Churn Risk</option>
          <option value="order_count">Sort: Orders</option>
          <option value="created_at">Sort: Recent</option>
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(c => (
            <Link key={c.id} href={`/twins/${c.id}`}>
              <div className="xeno-card cursor-pointer hover:shadow-md transition-all group h-full">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="text-sm font-semibold text-[var(--text-primary)] group-hover:text-violet-600 transition-colors">{c.name}</div>
                    <div className="text-xs text-[var(--text-muted)]">{c.city} · {c.order_count} orders</div>
                  </div>
                  {c.twin && (
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${getChurnColor(c.twin.churn_probability || 0)}`}>
                      {((c.twin.churn_probability || 0) * 100).toFixed(0)}% churn
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="bg-[var(--bg-muted)] rounded-lg p-2.5">
                    <div className="text-[10px] text-[var(--text-muted)] mb-0.5">Total LTV</div>
                    <div className="text-sm font-bold text-[var(--text-primary)]">{formatCurrency(c.total_spend || 0)}</div>
                  </div>
                  <div className="bg-[var(--bg-muted)] rounded-lg p-2.5">
                    <div className="text-[10px] text-[var(--text-muted)] mb-0.5">LTV 90d</div>
                    <div className="text-sm font-bold text-[var(--text-primary)]">{formatCurrency(c.twin?.predicted_ltv_90d || 0)}</div>
                  </div>
                </div>

                {c.twin?.narrative_summary && (
                  <p className="text-[11px] text-[var(--text-secondary)] line-clamp-2 leading-relaxed">{c.twin.narrative_summary}</p>
                )}

                {c.twin?.channel_affinity && (
                  <div className="flex gap-2 mt-3">
                    {Object.entries(c.twin.channel_affinity as Record<string, number>).map(([ch, score]) => (
                      <div key={ch} className="flex-1 text-center">
                        <div className="text-[9px] text-[var(--text-muted)] capitalize">{ch}</div>
                        <div className="text-[11px] font-semibold text-[var(--text-primary)]">{formatPct(score)}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
