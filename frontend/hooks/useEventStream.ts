'use client';
import { useState, useEffect, useRef, useCallback } from 'react';
import { LiveEvent } from '@/lib/types';

export function useEventStream(campaignId?: string) {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (esRef.current) esRef.current.close();

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const url = campaignId
      ? `${API_BASE}/api/v1/events/stream/${campaignId}`
      : `${API_BASE}/api/v1/events/stream`;

    const es = new EventSource(url);
    esRef.current = es;

    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as LiveEvent;
        setEvents(prev => [data, ...prev].slice(0, 500));
      } catch {}
    };
  }, [campaignId]);

  useEffect(() => {
    connect();
    return () => { esRef.current?.close(); };
  }, [connect]);

  const clear = useCallback(() => setEvents([]), []);
  return { events, connected, clear };
}
