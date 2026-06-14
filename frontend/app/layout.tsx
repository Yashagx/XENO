import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/layout/Sidebar';
import { XenoPilot } from '@/components/xenopilot/XenoPilot';

export const metadata: Metadata = {
  title: 'Xeno Oracle — AI Marketing Intelligence',
  description: 'An autonomous AI marketing strategist that thinks, predicts, and acts.',
  keywords: 'AI marketing, CRM, autonomous agents, campaign automation, customer intelligence',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ backgroundColor: 'var(--bg-base)', color: 'var(--text-primary)' }} className="min-h-screen flex">
        <Sidebar />
        <main style={{ marginLeft: '240px', minHeight: '100vh', flex: 1, overflowY: 'auto' }}>
          {children}
        </main>
        <XenoPilot />
      </body>
    </html>
  );
}

