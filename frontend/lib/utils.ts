export function formatCurrency(amount: number): string {
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount.toFixed(0)}`;
}

export function formatPct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatDays(days?: number): string {
  if (!days) return 'N/A';
  if (days === 0) return 'Today';
  if (days === 1) return '1 day ago';
  if (days < 30) return `${days}d ago`;
  if (days < 365) return `${Math.floor(days / 30)}mo ago`;
  return `${Math.floor(days / 365)}yr ago`;
}

export function getChurnColor(churn: number): string {
  if (churn > 0.7) return '#f43f5e';
  if (churn > 0.4) return '#f59e0b';
  return '#10b981';
}

export function getStatusColor(status: string): string {
  const map: Record<string, string> = {
    draft: '#64748b', segmenting: '#6366f1', strategizing: '#a855f7',
    writing: '#f59e0b', simulating: '#00D4FF', ready: '#10b981',
    executing: '#f59e0b', completed: '#10b981', failed: '#f43f5e',
  };
  return map[status] || '#64748b';
}

export function getConfidenceLabel(c: number): string {
  if (c >= 0.75) return 'High';
  if (c >= 0.5) return 'Medium';
  return 'Low';
}

export function getConfidenceColor(c: number): string {
  if (c >= 0.75) return '#10b981';
  if (c >= 0.5) return '#f59e0b';
  return '#f43f5e';
}

export function timeAgo(dateStr?: string): string {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function getChannelIcon(channel: string): string {
  const map: Record<string, string> = { email: '📧', sms: '💬', whatsapp: '📱', rcs: '🔵' };
  return map[channel] || '📨';
}

export function getAgentIcon(agentId: string): string {
  const map: Record<string, string> = {
    intent_parser: '🧠', memory_agent: '💾', segmentation_agent: '🎯',
    persona_agent: '👥', strategy_agent: '♟️', copywriter_agent: '✍️',
    channel_agent: '📡', simulator_agent: '⏱️', execution_agent: '🚀',
    learning_agent: '📚', insight_agent: '💡', orchestrator: '🎼',
  };
  return map[agentId] || '🤖';
}
