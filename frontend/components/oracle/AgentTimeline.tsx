'use client';
import { LiveEvent } from '@/lib/types';
import { getAgentIcon, getConfidenceColor } from '@/lib/utils';
import { Loader2, XCircle } from 'lucide-react';

const AGENT_ORDER = [
  { id: 'intent_parser', name: 'Intent Parser' },
  { id: 'memory_agent', name: 'Memory Agent' },
  { id: 'segmentation_agent', name: 'Segmentation Agent' },
  { id: 'persona_agent', name: 'Persona Agent' },
  { id: 'strategy_agent', name: 'Strategy Agent' },
  { id: 'copywriter_agent', name: 'Copywriter Agent' },
  { id: 'simulator_agent', name: 'Campaign Simulator' },
  { id: 'execution_agent', name: 'Execution Agent' },
  { id: 'learning_agent', name: 'Learning Agent' },
  { id: 'insight_agent', name: 'Insight Agent' },
];

interface Props {
  events: LiveEvent[];
  campaignStatus?: string;
}

export function AgentTimeline({ events, campaignStatus }: Props) {
  const latestByAgent: Record<string, LiveEvent> = {};
  [...events].reverse().forEach(e => {
    if (e.agent) latestByAgent[e.agent] = e;
  });

  const activeAgent = Object.entries(latestByAgent).find(([, e]) => e.status === 'running')?.[0];

  if (events.length === 0) {
    return (
      <div className="text-center py-8 text-[var(--text-muted)]">
        <div className="text-3xl mb-2">⏳</div>
        <p className="text-xs">Agent pipeline will appear here once started</p>
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {AGENT_ORDER.map((agent, idx) => {
        const ev = latestByAgent[agent.id];
        const icon = getAgentIcon(agent.id);
        const isActive = activeAgent === agent.id;
        const isCompleted = ev?.status === 'completed' || ev?.status === 'ready_for_approval';
        const isFailed = ev?.status === 'failed';
        const isPending = !ev;

        return (
          <div key={agent.id} className="flex gap-3">
            {/* Timeline */}
            <div className="flex flex-col items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0 z-10 transition-all
                ${isCompleted ? 'bg-emerald-100 border border-emerald-300' : ''}
                ${isActive ? 'bg-indigo-100 border border-indigo-300' : ''}
                ${isFailed ? 'bg-rose-100 border border-rose-300' : ''}
                ${isPending ? 'bg-[var(--bg-muted)] border border-[var(--border)]' : ''}
              `}>
                {isActive ? (
                  <Loader2 className="w-3.5 h-3.5 text-indigo-500 animate-spin" />
                ) : isCompleted ? (
                  <span>{icon}</span>
                ) : isFailed ? (
                  <XCircle className="w-3.5 h-3.5 text-rose-500" />
                ) : (
                  <span className="opacity-30 text-xs">{icon}</span>
                )}
              </div>
              {idx < AGENT_ORDER.length - 1 && (
                <div className={`w-px flex-1 my-1 ${isCompleted ? 'bg-emerald-200' : 'bg-[var(--border)]'}`} style={{minHeight: '20px'}} />
              )}
            </div>

            {/* Content */}
            <div className={`flex-1 pb-3.5 ${isPending ? 'opacity-30' : ''}`}>
              <div className="flex items-center gap-2 mb-0.5">
                <span className={`text-xs font-semibold ${
                  isActive ? 'text-indigo-600' :
                  isCompleted ? 'text-[var(--text-primary)]' :
                  'text-[var(--text-muted)]'
                }`}>{agent.name}</span>
                {isActive && (
                  <span className="text-[10px] bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded-full font-semibold">Running</span>
                )}
                {isCompleted && ev?.confidence && (
                  <span className="text-[10px] font-semibold" style={{color: getConfidenceColor(ev.confidence)}}>
                    {Math.round(ev.confidence * 100)}%
                  </span>
                )}
              </div>
              {ev && (
                <p className="text-[11px] text-[var(--text-secondary)] leading-relaxed">{ev.message}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
