import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/components/layout/AuthProvider';

export const metadata: Metadata = {
  title: 'Xeno Oracle — AI Marketing Intelligence',
  description: 'An autonomous AI marketing strategist that thinks, predicts, and acts.',
  keywords: 'AI marketing, CRM, autonomous agents, campaign automation, customer intelligence',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ backgroundColor: 'var(--bg-base)', color: 'var(--text-primary)' }} className="min-h-screen flex">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
