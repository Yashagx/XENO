'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { isLoggedIn } from '@/lib/auth';
import { Sidebar } from '@/components/layout/Sidebar';
import { XenoPilot } from '@/components/xenopilot/XenoPilot';

const PUBLIC_ROUTES = ['/login', '/signup'];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  const isPublicRoute = PUBLIC_ROUTES.includes(pathname);
  const loggedIn = mounted ? isLoggedIn() : false;

  useEffect(() => {
    setMounted(true);
    const loggedIn = isLoggedIn();
    if (!loggedIn && !PUBLIC_ROUTES.includes(pathname)) {
      router.push('/login');
    } else if (loggedIn && PUBLIC_ROUTES.includes(pathname)) {
      router.push('/');
    }
  }, [pathname, router]);

  // Prevent flash of unauthenticated content
  if (!mounted) {
    return null;
  }

  // Public pages: no sidebar, no xenopilot — just render the page
  if (isPublicRoute) {
    return <>{children}</>;
  }

  // Protected pages: show sidebar + main layout + xenopilot
  return (
    <>
      <Sidebar />
      <main style={{ marginLeft: '240px', minHeight: '100vh', flex: 1, overflowY: 'auto' }}>
        {children}
      </main>
      <XenoPilot />
    </>
  );
}
