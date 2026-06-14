'use client';
import { CampaignStats } from '@/lib/types';
import { formatPct } from '@/lib/utils';

interface Props {
  stats: CampaignStats;
}

const STAGES = [
  { key: 'total_sent', label: 'Sent', color: '#6366f1' },
  { key: 'delivered', label: 'Delivered', color: '#8b5cf6' },
  { key: 'opened', label: 'Opened', color: '#a855f7' },
  { key: 'clicked', label: 'Clicked', color: '#00D4FF' },
  { key: 'converted', label: 'Converted', color: '#10b981' },
];

export function FunnelChart({ stats }: Props) {
  const maxVal = stats.total_sent || 1;

  return (
    <div className="space-y-2">
      {STAGES.map((stage, idx) => {
        const val = (stats as any)[stage.key] || 0;
        const pct = val / maxVal;
        const prevKey = idx > 0 ? STAGES[idx - 1].key : null;
        const prevVal = prevKey ? (stats as any)[prevKey] || 1 : maxVal;
        const stepRate = val / (prevVal || 1);

        return (
          <div key={stage.key}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-[#8899bb]">{stage.label}</span>
              <div className="flex items-center gap-3">
                {idx > 0 && (
                  <span className="text-xs text-[#4a5568]">{formatPct(stepRate)} step</span>
                )}
                <span className="text-sm font-bold text-white">{val.toLocaleString()}</span>
              </div>
            </div>
            <div className="h-8 bg-[#0D1320] rounded-lg overflow-hidden relative">
              <div
                className="h-full rounded-lg flex items-center px-3 transition-all duration-700"
                style={{
                  width: `${Math.max(pct * 100, 2)}%`,
                  background: `linear-gradient(90deg, ${stage.color}33, ${stage.color}66)`,
                  borderLeft: `3px solid ${stage.color}`,
                  boxShadow: `inset 0 0 10px ${stage.color}22`
                }}
              >
                <span className="text-xs font-mono" style={{ color: stage.color }}>
                  {formatPct(pct)}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
