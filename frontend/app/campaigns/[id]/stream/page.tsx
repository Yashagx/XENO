'use client';
import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Campaign, CampaignStats } from '@/lib/types';
import { FunnelChart } from '@/components/campaigns/FunnelChart';
import { useEventStream } from '@/hooks/useEventStream';
import { getChannelIcon, timeAgo } from '@/lib/utils';
import { ArrowLeft, Radio, Zap, Activity } from 'lucide-react';
import Link from 'next/link';

const EVENT_COLORS: Record<string, string> = {
  delivered: '#6366f1', opened: '#a855f7', clicked: '#00D4FF',
  converted: '#10b981', failed: '#f43f5e', bounced: '#f59e0b',
  agent_step: '#8899bb',
};

export default function LiveStreamPage() {
  const { id } = useParams<{ id: string }>();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [stats, setStats] = useState<CampaignStats | null>(null);
  const { events, connected, clear } = useEventStream(id);

  const messageEvents = events.filter(e => e.type === 'message_event');
  const agentEvents = events.filter(e => e.type === 'agent_step');

  useEffect(() => {
    if (!id) return;
    const load = async () => {
      try {
        const [c, s] = await Promise.all([
          api.getCampaign(id) as Promise<Campaign>,
          api.getCampaignStats(id) as Promise<CampaignStats>,
        ]);
        setCampaign(c);
        setStats(s);
      } catch {}
    };
    load();
    const t = setInterval(async () => {
      try { setStats(await api.getCampaignStats(id) as CampaignStats); } catch {}
    }, 3000);
    return () => clearInterval(t);
  }, [id]);

  return (
    <div className="min-h-screen p-6">
      <div className="flex items-center gap-4 mb-8">
        <Link href={`/campaigns/${id}`} className="text-[#8899bb] hover:text-white">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Radio className="w-5 h-5 text-cyan-400" /> Live Event Stream
          </h1>
          <p className="text-xs text-[#8899bb] mt-0.5">{campaign?.name}</p>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <span className={`w-2.5 h-2.5 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-[#4a5568]'}`} />
          <span className="text-sm text-[#8899bb]">{connected ? 'Live' : 'Disconnected'}</span>
          <span className="text-xs text-[#4a5568]">· {events.length} events</span>
          <button onClick={clear} className="text-xs text-[#4a5568] hover:text-white px-2 py-1 rounded border border-[#1e2d45] hover:border-[#2a3f5f] transition-all">Clear</button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Event feed */}
        <div className="xl:col-span-2">
          <div className="glass rounded-xl overflow-hidden" style={{ height: '620px', display: 'flex', flexDirection: 'column' }}>
            <div className="px-4 py-3 border-b border-[#1e2d45] flex items-center gap-2 shrink-0">
              <Zap className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-semibold">Event Feed</span>
              <span className="ml-auto text-xs text-[#4a5568]">{messageEvents.length} delivery events · {agentEvents.length} agent steps</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-1">
              {events.length === 0 ? (
                <div className="text-center py-20 text-[#4a5568]">
                  <div className="text-4xl mb-3 animate-pulse">📡</div>
                  <p className="text-sm">Waiting for events...</p>
                  <p className="text-xs mt-1">Events will stream here in real-time via SSE</p>
                </div>
              ) : (
                events.slice(0, 300).map((e, i) => {
                  const color = e.event_type ? EVENT_COLORS[e.event_type] : (e.type === 'agent_step' ? '#6366f1' : '#8899bb');
                  const isAgent = e.type === 'agent_step';
                  return (
                    <div key={i} className="flex items-start gap-3 py-1.5 border-b border-[#0D1320] animate-slide-in">
                      <div className="w-1.5 h-1.5 rounded-full mt-2 shrink-0" style={{ backgroundColor: color }} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          {isAgent ? (
                            <>
                              <span className="text-xs font-medium text-indigo-300">🤖 {e.agent_name || e.agent}</span>
                              {e.status && <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400">{e.status}</span>}
                            </>
                          ) : (
                            <>
                              <span className="text-xs font-mono font-semibold" style={{ color }}>
                                {e.event_type?.toUpperCase()}
                              </span>
                              {e.channel && (
                                <span className="text-[10px] text-[#4a5568]">{getChannelIcon(e.channel)} {e.channel}</span>
                              )}
                            </>
                          )}
                          <span className="text-[10px] text-[#4a5568] ml-auto">{timeAgo(e.timestamp)}</span>
                        </div>
                        <p className="text-xs text-[#8899bb] mt-0.5 truncate">
                          {isAgent ? e.message : `msg:${e.message_id?.slice(0, 8)}… cust:${e.customer_id?.slice(0, 8)}…`}
                        </p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Right: live stats */}
        <div className="space-y-4">
          {stats && (
            <>
              <div className="xeno-card">
                <div className="text-sm font-semibold text-[#8899bb] uppercase tracking-wider mb-4">
                  <Activity className="w-4 h-4 inline mr-2" />Live Funnel
                </div>
                <FunnelChart stats={stats} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: 'Sent', value: stats.total_sent, color: '#6366f1' },
                  { label: 'Delivered', value: stats.delivered, color: '#8b5cf6' },
                  { label: 'Opened', value: stats.opened, color: '#a855f7' },
                  { label: 'Clicked', value: stats.clicked, color: '#00D4FF' },
                  { label: 'Converted', value: stats.converted, color: '#10b981' },
                  { label: 'Failed', value: stats.failed, color: '#f43f5e' },
                ].map(m => (
                  <div key={m.label} className="xeno-card text-center py-3">
                    <div className="text-xl font-bold" style={{ color: m.color }}>{m.value.toLocaleString()}</div>
                    <div className="text-xs text-[#8899bb] mt-1">{m.label}</div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
