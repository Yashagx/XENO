'use client';
import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Customer, CustomerTwin } from '@/lib/types';
import { formatCurrency, formatDays, getChurnColor, getConfidenceColor, formatPct } from '@/lib/utils';
import { ArrowLeft, GitBranch } from 'lucide-react';
import Link from 'next/link';

function AffinityBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-[#8899bb] w-32 shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-[#0D1320] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${Math.min(100, value * 100)}%`, backgroundColor: color, boxShadow: `0 0 6px ${color}88` }}
        />
      </div>
      <span className="text-sm font-mono text-white w-12 text-right">{formatPct(value)}</span>
    </div>
  );
}

export default function TwinDetail() {
  const { id } = useParams<{ id: string }>();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [twin, setTwin] = useState<CustomerTwin | null>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    if (!id) return;
    Promise.all([
      api.getCustomer(id) as Promise<Customer>,
      api.getTwin(id) as Promise<CustomerTwin>,
      api.getTwinHistory(id) as Promise<any>,
    ]).then(([c, t, h]) => {
      setCustomer(c);
      setTwin(t);
      setHistory(h.history || []);
    }).catch(() => {});
  }, [id]);

  if (!customer || !twin) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-3" />
          <p className="text-[#4a5568]">Loading twin profile...</p>
        </div>
      </div>
    );
  }

  const initials = customer.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2).toUpperCase();
  const churnColor = getChurnColor(twin.churn_probability);

  return (
    <div className="min-h-screen p-6">
      <div className="flex items-center gap-3 mb-8">
        <Link href="/twins" className="text-[#8899bb] hover:text-white"><ArrowLeft className="w-5 h-5" /></Link>
        <h1 className="text-xl font-bold text-white">Customer Digital Twin</h1>
        <span className="text-xs font-mono text-[#4a5568] bg-[#0D1320] px-2 py-1 rounded border border-[#1e2d45]">v{twin.version}</span>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left: Profile + affinities */}
        <div className="xl:col-span-2 space-y-6">
          {/* Profile card */}
          <div className="xeno-card">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/30 to-cyan-500/20 border border-indigo-500/30 flex items-center justify-center text-2xl font-bold text-indigo-300 shrink-0">
                {initials}
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-white">{customer.name}</h2>
                <div className="text-sm text-[#8899bb]">{customer.email}</div>
                <div className="text-sm text-[#4a5568]">{customer.city} · {customer.phone}</div>
                {twin.narrative_summary && (
                  <p className="mt-3 text-sm text-[#8899bb] leading-relaxed border-l-2 border-indigo-500/40 pl-3 italic">
                    {twin.narrative_summary}
                  </p>
                )}
              </div>
              <div className="text-right shrink-0">
                <div className="text-3xl font-bold" style={{ color: churnColor }}>{formatPct(twin.churn_probability)}</div>
                <div className="text-xs text-[#8899bb]">Churn Risk</div>
                <div className="text-xs mt-1" style={{ color: getConfidenceColor(twin.purchase_intent_score) }}>
                  {formatPct(twin.purchase_intent_score)} intent
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-[#1e2d45]">
              {[
                { label: 'Total Spend', value: formatCurrency(customer.total_spend) },
                { label: 'Orders', value: String(customer.order_count) },
                { label: 'Last Order', value: formatDays(customer.last_order_days) },
                { label: 'Predicted LTV 90d', value: formatCurrency(twin.predicted_ltv_90d) },
                { label: 'Purchase Intent', value: formatPct(twin.purchase_intent_score) },
                { label: 'Twin Confidence', value: formatPct(twin.confidence_score) },
              ].map(m => (
                <div key={m.label}>
                  <div className="text-xs text-[#4a5568]">{m.label}</div>
                  <div className="text-sm font-bold text-white mt-0.5">{m.value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Channel affinities */}
          <div className="xeno-card">
            <h3 className="text-sm font-semibold text-[#8899bb] uppercase tracking-wider mb-4">📡 Channel Affinities</h3>
            <div className="space-y-4">
              <AffinityBar label="📧 Email" value={twin.channel_affinity?.email || 0} color="#6366f1" />
              <AffinityBar label="💬 SMS" value={twin.channel_affinity?.sms || 0} color="#a855f7" />
              <AffinityBar label="📱 WhatsApp" value={twin.channel_affinity?.whatsapp || 0} color="#10b981" />
            </div>
          </div>

          {/* Category affinities */}
          {Object.keys(twin.category_affinity || {}).length > 0 && (
            <div className="xeno-card">
              <h3 className="text-sm font-semibold text-[#8899bb] uppercase tracking-wider mb-4">🛍️ Category Affinities</h3>
              <div className="space-y-3">
                {Object.entries(twin.category_affinity)
                  .sort((a, b) => b[1] - a[1])
                  .map(([cat, val]) => (
                    <AffinityBar key={cat} label={cat} value={val} color="#00D4FF" />
                  ))}
              </div>
            </div>
          )}

          {/* Recent orders */}
          {(customer as any).recent_orders?.length > 0 && (
            <div className="xeno-card">
              <h3 className="text-sm font-semibold text-[#8899bb] uppercase tracking-wider mb-4">🛒 Recent Orders</h3>
              <div className="space-y-2">
                {(customer as any).recent_orders.map((o: any) => (
                  <div key={o.id} className="flex items-center justify-between py-2.5 px-3 rounded-lg bg-[#0D1320]">
                    <div>
                      <div className="text-sm font-medium text-white">{o.order_number}</div>
                      <div className="text-xs text-[#4a5568]">{o.channel} · {new Date(o.ordered_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</div>
                    </div>
                    <div className="text-sm font-bold text-white">{formatCurrency(o.total)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Personality + history */}
        <div className="space-y-6">
          <div className="xeno-card">
            <h3 className="text-sm font-semibold text-[#8899bb] uppercase tracking-wider mb-4">🧠 Personality Profile</h3>
            <div className="space-y-4">
              {[
                { label: 'Price Sensitivity', value: twin.price_sensitivity, color: '#f59e0b' },
                { label: 'Urgency Responsiveness', value: twin.urgency_responsiveness, color: '#f43f5e' },
                { label: 'Social Proof Affinity', value: twin.social_proof_affinity, color: '#00D4FF' },
                { label: 'Brand Loyalty', value: (twin as any).brand_affinity || 0.5, color: '#a855f7' },
              ].map(trait => (
                <div key={trait.label}>
                  <div className="flex justify-between mb-1">
                    <span className="text-xs text-[#8899bb]">{trait.label}</span>
                    <span className="text-xs font-mono text-white">{formatPct(trait.value)}</span>
                  </div>
                  <div className="h-1.5 bg-[#0D1320] rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-500" style={{ width: `${trait.value * 100}%`, backgroundColor: trait.color }} />
                  </div>
                </div>
              ))}
              <div className="pt-3 border-t border-[#1e2d45]">
                <div className="text-xs text-[#4a5568]">Communication Style</div>
                <div className="text-sm font-semibold text-white capitalize mt-1 flex items-center gap-2">
                  {twin.communication_style}
                  <span className="text-[10px] font-mono text-[#4a5568] bg-[#0D1320] px-2 py-0.5 rounded">preferred tone</span>
                </div>
              </div>
            </div>
          </div>

          {/* Twin meta */}
          <div className="xeno-card">
            <h3 className="text-sm font-semibold text-[#8899bb] uppercase tracking-wider mb-4">📊 Twin Metadata</h3>
            <div className="space-y-2">
              {[
                { label: 'Version', value: `v${twin.version}` },
                { label: 'Confidence', value: formatPct(twin.confidence_score) },
                { label: 'Next Purchase (est.)', value: `${twin.predicted_next_purchase_days || 'N/A'} days` },
                { label: 'Last Updated', value: twin.updated_at ? new Date(twin.updated_at).toLocaleDateString('en-IN') : 'N/A' },
              ].map(m => (
                <div key={m.label} className="flex justify-between py-1.5 border-b border-[#0D1320]">
                  <span className="text-xs text-[#4a5568]">{m.label}</span>
                  <span className="text-xs font-mono text-white">{m.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Version history */}
          {history.length > 0 && (
            <div className="xeno-card">
              <h3 className="text-sm font-semibold text-[#8899bb] uppercase tracking-wider mb-4 flex items-center gap-2">
                <GitBranch className="w-4 h-4" /> Twin Version History
              </h3>
              <div className="space-y-2">
                {history.slice(0, 10).map((h: any, i: number) => (
                  <div key={i} className="flex items-start gap-2 py-2 border-b border-[#0D1320] last:border-0">
                    <span className="text-xs font-mono text-indigo-400 shrink-0">v{h.version}</span>
                    <div className="flex-1">
                      <div className="text-xs text-[#8899bb]">{h.change_reason || 'Profile update'}</div>
                      <div className="text-[10px] text-[#4a5568]">{h.changed_at ? new Date(h.changed_at).toLocaleDateString('en-IN') : ''}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
