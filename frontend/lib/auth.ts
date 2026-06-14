export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'marketer' | 'viewer';
}

export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('xeno_token');
};

export const getUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  try {
    const u = localStorage.getItem('xeno_user');
    return u ? JSON.parse(u) : null;
  } catch {
    return null;
  }
};

export const isLoggedIn = (): boolean => !!getToken();

export const logout = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('xeno_token');
  localStorage.removeItem('xeno_user');
  document.cookie = 'xeno_token=; Max-Age=0; path=/';
  window.location.href = '/login';
};

export const hasRole = (role: string): boolean => getUser()?.role === role;

export const setSession = (token: string, user: User): void => {
  localStorage.setItem('xeno_token', token);
  localStorage.setItem('xeno_user', JSON.stringify(user));
  // Set cookie for middleware
  const expires = new Date(Date.now() + 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `xeno_token=${token}; expires=${expires}; path=/`;
};
