'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Zap, LayoutDashboard, Users, TrendingUp, Brain, LogOut, Cloud } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getUser, logout, User } from '@/lib/auth';

const navItems = [
  { href: '/', icon: Zap, label: 'Oracle Command' },
  { href: '/campaigns', icon: LayoutDashboard, label: 'Campaigns' },
  { href: '/twins', icon: Users, label: 'Twin Explorer' },
  { href: '/insights', icon: TrendingUp, label: 'Learning Console' },
];

const roleColors: Record<string, { bg: string; text: string; label: string }> = {
  admin: { bg: '#eef0fe', text: '#6366f1', label: 'Admin' },
  marketer: { bg: '#ecfdf5', text: '#059669', label: 'Marketer' },
  viewer: { bg: '#f3f4f6', text: '#6b7280', label: 'Viewer' },
};

export function Sidebar() {
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [awsOpen, setAwsOpen] = useState(false);
  const [awsStatus, setAwsStatus] = useState<any>(null);

  useEffect(() => {
    setUser(getUser());
  }, []);

  useEffect(() => {
    if (awsOpen && !awsStatus) {
      fetch((process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1/aws/status', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('xeno_token')}` }
      })
        .then(r => r.json())
        .then(setAwsStatus)
        .catch(() => setAwsStatus(null));
    }
  }, [awsOpen]);

  const initials = user?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || '?';
  const roleStyle = roleColors[user?.role || 'viewer'];

  return (
    <aside className="sidebar" style={{ position: 'fixed', top: 0, left: 0, width: '240px', height: '100vh', display: 'flex', flexDirection: 'column', zIndex: 50 }}>
      {/* Logo */}
      <div className="px-5 py-5 border-b border-[var(--border)]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-indigo-100 flex items-center justify-center">
            <Brain className="w-4 h-4 text-indigo-600" />
          </div>
          <div>
            <div className="text-sm font-bold text-[var(--text-primary)] tracking-wide">Xeno Oracle</div>
            <div className="text-[10px] text-[var(--text-muted)] font-medium uppercase tracking-widest">AI Marketing OS</div>
          </div>
        </div>
      </div>

      {/* Status indicator */}
      <div className="px-4 py-3 border-b border-[var(--border)]">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--emerald-light)]">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs text-emerald-700 font-medium">System Online</span>
          <span className="ml-auto text-[10px] text-emerald-500 font-mono">v2.0</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest px-3 py-2 font-semibold">Menu</div>
        {navItems.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
                ${active
                  ? 'bg-[var(--accent-light)] text-[var(--accent)] border border-indigo-100'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
                }
              `}
            >
              <Icon className={`w-4 h-4 ${active ? 'text-indigo-500' : 'text-[var(--text-muted)]'}`} />
              {label}
              {active && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-500" />}
            </Link>
          );
        })}
      </nav>

      {/* AWS Status Panel */}
      <div className="px-3 pb-2">
        <button
          onClick={() => setAwsOpen(!awsOpen)}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] transition-all"
        >
          <Cloud className="w-3.5 h-3.5 text-[var(--text-muted)]" />
          <span>AWS Services</span>
          <span className="ml-auto text-[10px]">{awsOpen ? '▲' : '▼'}</span>
        </button>
        {awsOpen && (
          <div className="mt-1 rounded-lg border border-[var(--border)] bg-[var(--bg-muted)] p-2 space-y-1">
            {awsStatus ? (
              [
                { key: 's3', label: 'S3', detail: awsStatus.s3?.bucket || '' },
                { key: 'ses', label: 'SES', detail: awsStatus.ses?.sender ? 'Configured' : 'Not set' },
                { key: 'sns', label: 'SNS', detail: awsStatus.sns?.connected ? 'Topic active' : 'Not set' },
                { key: 'cloudwatch', label: 'CW', detail: awsStatus.cloudwatch?.connected ? 'Metrics live' : 'Off' },
                { key: 'secrets_manager', label: 'SM', detail: awsStatus.secrets_manager?.connected ? 'Connected' : 'Off' },
              ].map(({ key, label, detail }) => {
                const connected = awsStatus[key]?.connected;
                return (
                  <div key={key} className="flex items-center gap-2 px-2 py-1">
                    <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${connected ? 'bg-emerald-500' : 'bg-gray-300'}`} />
                    <span className="text-[10px] font-semibold text-[var(--text-secondary)] w-6">{label}</span>
                    <span className="text-[10px] text-[var(--text-muted)] truncate">{detail}</span>
                  </div>
                );
              })
            ) : (
              <div className="px-2 py-1 text-[10px] text-[var(--text-muted)]">Loading...</div>
            )}
          </div>
        )}
      </div>

      {/* User Block */}
      {user && (
        <div className="px-3 pb-3">
          <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-[var(--bg-muted)] border border-[var(--border)]">
            <div style={{
              width: '32px', height: '32px', borderRadius: '50%',
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'white', fontSize: '11px', fontWeight: 700, flexShrink: 0,
            }}>
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-[var(--text-primary)] truncate">{user.name}</div>
              <span style={{
                display: 'inline-block', padding: '0 6px', borderRadius: '9999px',
                background: roleStyle.bg, color: roleStyle.text,
                fontSize: '9px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em',
                marginTop: '2px',
              }}>
                {roleStyle.label}
              </span>
            </div>
            <button
              onClick={logout}
              title="Logout"
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', borderRadius: '6px', color: 'var(--text-muted)' }}
              onMouseEnter={e => (e.currentTarget.style.color = '#e11d48')}
              onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
            >
              <LogOut size={13} />
            </button>
          </div>
        </div>
      )}

      {/* Bottom */}
      <div className="px-4 py-3 border-t border-[var(--border)]">
        <div className="text-[10px] text-[var(--text-muted)] text-center">
          RFC-001 · Yash Agarwal
        </div>
      </div>
    </aside>
  );
}
