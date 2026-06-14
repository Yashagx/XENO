'use client';
import { Customer } from '@/lib/types';
import { formatCurrency, formatDays, getChurnColor, getConfidenceColor } from '@/lib/utils';
import Link from 'next/link';
import { TrendingDown, TrendingUp, Mail, MessageSquare, Phone } from 'lucide-react';

function AffinityBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-xs text-[#8899bb]">{label}</span>
        <span className="text-xs font-mono text-white">{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="h-1.5 bg-[#0D1320] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${value * 100}%`,
            backgroundColor: color,
            boxShadow: `0 0 6px ${color}88`
          }}
        />
      </div>
    </div>
  );
}

export function TwinCard({ customer }: { customer: Customer }) {
  const twin = customer.twin;
  const churnColor = twin ? getChurnColor(twin.churn_probability) : '#94a3b8';
  const initials = customer.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();

  return (
    <Link href={`/twins/${customer.id}`}>
      <div className="xeno-card hover:border-[#2a3f5f] hover:glow-indigo cursor-pointer group transition-all duration-200 h-full">
        {/* Header */}
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/30 to-cyan-500/20 border border-indigo-500/30 flex items-center justify-center text-sm font-bold text-indigo-300 shrink-0">
            {initials}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-white text-sm truncate group-hover:text-cyan-300 transition-colors">{customer.name}</div>
            <div className="text-xs text-[#8899bb] truncate">{customer.email}</div>
            <div className="text-xs text-[#4a5568]">{customer.city}</div>
          </div>
          {twin && (
            <div className="flex flex-col items-end gap-1">
              <span className="text-xs font-mono" style={{ color: churnColor }}>
                {(twin.churn_probability * 100).toFixed(0)}% churn
              </span>
              {twin.churn_probability > 0.6 ? (
                <TrendingDown className="w-3.5 h-3.5" style={{ color: churnColor }} />
              ) : (
                <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
              )}
            </div>
          )}
        </div>

        {/* Spend + Orders */}
        <div className="flex gap-3 mb-4">
          <div className="flex-1 rounded-lg bg-[#0D1320] px-3 py-2">
            <div className="text-xs text-[#4a5568] mb-0.5">Total Spend</div>
            <div className="font-bold text-white text-sm">{formatCurrency(customer.total_spend)}</div>
          </div>
          <div className="flex-1 rounded-lg bg-[#0D1320] px-3 py-2">
            <div className="text-xs text-[#4a5568] mb-0.5">Orders</div>
            <div className="font-bold text-white text-sm">{customer.order_count}</div>
          </div>
          <div className="flex-1 rounded-lg bg-[#0D1320] px-3 py-2">
            <div className="text-xs text-[#4a5568] mb-0.5">Last Order</div>
            <div className="font-bold text-white text-sm">{formatDays(customer.last_order_days)}</div>
          </div>
        </div>

        {/* Channel affinities */}
        {twin && (
          <div className="space-y-2">
            <AffinityBar label="📧 Email" value={twin.channel_affinity?.email || 0} color="#6366f1" />
            <AffinityBar label="💬 SMS" value={twin.channel_affinity?.sms || 0} color="#a855f7" />
            <AffinityBar label="📱 WhatsApp" value={twin.channel_affinity?.whatsapp || 0} color="#10b981" />
          </div>
        )}

        {/* Narrative */}
        {twin?.narrative_summary && (
          <p className="mt-3 text-xs text-[#8899bb] leading-relaxed line-clamp-2">{twin.narrative_summary}</p>
        )}

        {/* Version badge */}
        {twin && (
          <div className="mt-3 flex items-center justify-between">
            <span className="text-[10px] font-mono text-[#4a5568]">Twin v{twin.version}</span>
            <span className="text-[10px] font-mono" style={{ color: getConfidenceColor(twin.confidence_score) }}>
              {(twin.confidence_score * 100).toFixed(0)}% confidence
            </span>
          </div>
        )}
      </div>
    </Link>
  );
}
