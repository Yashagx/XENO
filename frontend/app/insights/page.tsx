'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Insight } from '@/lib/types';
import { TrendingUp, Lightbulb, Target, BookOpen } from 'lucide-react';
import { timeAgo, formatPct } from '@/lib/utils';

export default function LearningConsole() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [selected, setSelected] = useState<Insight | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listInsights()
      .then((d: any) => {
        setInsights(d.insights || []);
        if (d.insights?.length > 0) setSelected(d.insights[0]);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center">
          <TrendingUp className="w-4 h-4 text-emerald-600" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-[var(--text-primary)]">Learning Console</h1>
          <p className="text-xs text-[var(--text-muted)] mt-0.5">AI-generated insights from completed campaigns</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin w-6 h-6 border-2 border-emerald-400 border-t-transparent rounded-full" />
        </div>
      ) : insights.length === 0 ? (
        <div className="xeno-card text-center py-24">
          <BookOpen className="w-10 h-10 text-[var(--text-muted)] mx-auto mb-3" />
          <p className="text-sm text-[var(--text-secondary)]">No insights yet</p>
          <p className="text-xs text-[var(--text-muted)] mt-1">Complete a campaign to see AI learning here.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Insights list */}
          <div className="space-y-2">
            <div className="text-[11px] text-[var(--text-muted)] uppercase tracking-wider mb-3">Campaigns ({insights.length})</div>
            {insights.map(ins => (
              <button
                key={ins.id}
                onClick={() => setSelected(ins)}
                className={`w-full text-left rounded-xl p-3.5 border transition-all ${
                  selected?.id === ins.id
                    ? 'border-indigo-300 bg-[var(--accent-light)] shadow-sm'
                    : 'border-[var(--border)] bg-white hover:shadow-sm hover:border-indigo-200'
                }`}
              >
                <div className="text-xs font-semibold text-[var(--text-primary)] truncate">{ins.campaign_name || 'Campaign'}</div>
                <div className="text-[11px] text-[var(--text-muted)] mt-1 line-clamp-2">{ins.content?.executive_summary}</div>
                <div className="flex items-center gap-2 mt-2">
                  {ins.content?.winning_element && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-medium">✓ {ins.content.winning_element}</span>
                  )}
                  <span className="text-[9px] text-[var(--text-muted)] ml-auto">{timeAgo(ins.generated_at)}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Insight detail */}
          {selected ? (
            <div className="xl:col-span-2 space-y-4 animate-fade-in">
              {/* Executive summary */}
              <div className="xeno-card border-indigo-200 bg-indigo-50">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-6 h-6 bg-indigo-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-3.5 h-3.5 text-indigo-600" />
                  </div>
                  <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wider">Executive Summary</span>
                </div>
                <p className="text-sm text-[var(--text-primary)] leading-relaxed font-medium">{selected.content?.executive_summary}</p>
                {selected.content?.actual_stats && (
                  <div className="flex gap-6 mt-4 pt-4 border-t border-indigo-200">
                    {[
                      { label: 'Open Rate', val: formatPct(selected.content.actual_stats.open_rate || 0) },
                      { label: 'Click Rate', val: formatPct(selected.content.actual_stats.click_rate || 0) },
                      { label: 'Conversion', val: formatPct(selected.content.actual_stats.conversion_rate || 0) },
                      { label: 'Total Sent', val: (selected.content.actual_stats.total_sent || 0).toLocaleString() },
                    ].map(m => (
                      <div key={m.label}>
                        <div className="text-[10px] text-indigo-500">{m.label}</div>
                        <div className="text-sm font-bold text-indigo-800">{m.val}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Key insights */}
              {selected.content?.key_insights?.length > 0 && (
                <div className="xeno-card">
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="w-4 h-4 text-amber-500" />
                    <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Key Insights</span>
                  </div>
                  <div className="space-y-2">
                    {selected.content.key_insights.map((insight: string, i: number) => (
                      <div key={i} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-amber-50">
                        <span className="text-amber-500 font-bold text-xs shrink-0 mt-0.5">{i + 1}</span>
                        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {selected.content?.next_campaign_recommendations?.length > 0 && (
                <div className="xeno-card">
                  <div className="flex items-center gap-2 mb-3">
                    <Target className="w-4 h-4 text-emerald-500" />
                    <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Next Campaign Recommendations</span>
                  </div>
                  <div className="space-y-2">
                    {selected.content.next_campaign_recommendations.map((rec: string, i: number) => (
                      <div key={i} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-emerald-50 border border-emerald-100">
                        <span className="text-emerald-500 text-xs shrink-0">✓</span>
                        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Win + improve */}
              {(selected.content?.winning_element || selected.content?.improvement_area) && (
                <div className="grid grid-cols-2 gap-4">
                  {selected.content.winning_element && (
                    <div className="xeno-card bg-emerald-50 border-emerald-200">
                      <div className="text-[10px] text-emerald-600 uppercase tracking-wider mb-1.5 font-semibold">🏆 What Worked</div>
                      <p className="text-xs text-[var(--text-primary)]">{selected.content.winning_element}</p>
                    </div>
                  )}
                  {selected.content.improvement_area && (
                    <div className="xeno-card bg-rose-50 border-rose-200">
                      <div className="text-[10px] text-rose-600 uppercase tracking-wider mb-1.5 font-semibold">📈 Improve Next</div>
                      <p className="text-xs text-[var(--text-primary)]">{selected.content.improvement_area}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="xl:col-span-2 flex items-center justify-center py-20 text-[var(--text-muted)] text-sm">
              Select an insight from the left to view details
            </div>
          )}
        </div>
      )}
    </div>
  );
}
