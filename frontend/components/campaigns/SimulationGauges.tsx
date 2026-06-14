'use client';
import { SimulationResult } from '@/lib/types';
import { formatPct, formatCurrency, getConfidenceColor } from '@/lib/utils';

function ArcGauge({ value, min, max, label, format = 'pct', color = '#00D4FF' }: {
  value: number; min: number; max: number; label: string;
  format?: 'pct' | 'currency' | 'number'; color?: string;
}) {
  const radius = 52;
  const circumference = Math.PI * radius;
  const pct = Math.max(0, Math.min(1, (value - min) / (max - min || 1)));
  const offset = circumference * (1 - pct);

  const fmt = format === 'pct' ? formatPct : format === 'currency' ? formatCurrency : (v: number) => v.toFixed(1);

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="130" height="80" viewBox="0 0 130 80">
        {/* Background arc */}
        <path
          d="M 15 70 A 52 52 0 0 1 115 70"
          fill="none"
          stroke="#1e2d45"
          strokeWidth="10"
          strokeLinecap="round"
        />
        {/* Value arc */}
        <path
          d="M 15 70 A 52 52 0 0 1 115 70"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${circumference}`}
          strokeDashoffset={`${offset}`}
          style={{ filter: `drop-shadow(0 0 6px ${color}66)`, transition: 'stroke-dashoffset 0.6s ease' }}
        />
        <text x="65" y="64" textAnchor="middle" fill="white" fontSize="16" fontWeight="700" fontFamily="Inter">
          {fmt(value)}
        </text>
      </svg>
      <span className="text-xs text-[#8899bb] text-center">{label}</span>
    </div>
  );
}

export function SimulationGauges({ sim }: { sim: SimulationResult }) {
  return (
    <div className="space-y-6">
      {/* Main gauges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="xeno-card flex flex-col items-center">
          <ArcGauge
            value={sim.open_rate.p50}
            min={0} max={0.7}
            label="Open Rate (P50)"
            color="#6366f1"
          />
          <div className="text-xs text-[#4a5568] mt-1 text-center">
            P10: {formatPct(sim.open_rate.p10)} · P90: {formatPct(sim.open_rate.p90)}
          </div>
        </div>

        <div className="xeno-card flex flex-col items-center">
          <ArcGauge
            value={sim.click_rate.p50}
            min={0} max={0.4}
            label="Click Rate (P50)"
            color="#a855f7"
          />
          <div className="text-xs text-[#4a5568] mt-1 text-center">
            P10: {formatPct(sim.click_rate.p10)} · P90: {formatPct(sim.click_rate.p90)}
          </div>
        </div>

        <div className="xeno-card flex flex-col items-center">
          <ArcGauge
            value={sim.conversion_rate.p50}
            min={0} max={0.15}
            label="Conversion (P50)"
            color="#10b981"
          />
          <div className="text-xs text-[#4a5568] mt-1 text-center">
            P10: {formatPct(sim.conversion_rate.p10)} · P90: {formatPct(sim.conversion_rate.p90)}
          </div>
        </div>

        <div className="xeno-card flex flex-col items-center">
          <ArcGauge
            value={sim.revenue_inr?.p50 || 0}
            min={0} max={(sim.revenue_inr?.p90 || 1) * 1.2}
            label="Revenue (P50)"
            format="currency"
            color="#f59e0b"
          />
          <div className="text-xs text-[#4a5568] mt-1 text-center">
            ROI: {sim.roi?.toFixed(1)}x
          </div>
        </div>
      </div>

      {/* Confidence indicator */}
      <div className="xeno-card">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold">Time Machine Confidence</span>
          <span className="text-sm font-bold" style={{ color: getConfidenceColor(sim.confidence) }}>
            {(sim.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="h-2 bg-[#1e2d45] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${sim.confidence * 100}%`,
              background: `linear-gradient(90deg, ${getConfidenceColor(sim.confidence)}, ${getConfidenceColor(sim.confidence)}aa)`,
              boxShadow: `0 0 10px ${getConfidenceColor(sim.confidence)}66`
            }}
          />
        </div>
        <p className="text-xs text-[#8899bb] mt-2">{sim.confidence_reason}</p>
      </div>

      {/* Alternatives */}
      {sim.alternatives && sim.alternatives.length > 0 && (
        <div className="xeno-card">
          <div className="text-sm font-semibold mb-3">Alternative Strategies</div>
          <div className="space-y-2">
            {sim.alternatives.map((alt, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[#0D1320]">
                <span className="text-emerald-400 font-bold text-sm">+{alt.predicted_uplift_pct}%</span>
                <div>
                  <p className="text-sm text-white">{alt.strategy}</p>
                  <p className="text-xs text-[#8899bb] mt-0.5">{alt.tradeoff}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
