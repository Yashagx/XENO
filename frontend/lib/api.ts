const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getAuthHeaders(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const token = localStorage.getItem('xeno_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...options?.headers,
      },
      ...options,
    });
    if (res.status === 401) {
      // Token expired or invalid — logout
      if (typeof window !== 'undefined') {
        localStorage.removeItem('xeno_token');
        localStorage.removeItem('xeno_user');
        document.cookie = 'xeno_token=; Max-Age=0; path=/';
        window.location.href = '/login';
      }
      throw new Error('Session expired. Please login again.');
    }
    if (!res.ok) {
      let errText = '';
      try { errText = await res.text(); } catch {}
      throw new Error(`API ${res.status}: ${errText.slice(0, 200)}`);
    }
    return res.json();
  } catch (err: any) {
    if (err?.message?.startsWith('API ') || err?.message?.startsWith('Session')) throw err;
    throw new Error(`Cannot reach backend at ${API_BASE}. Is the server running? (${err?.message})`);
  }
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    fetchApi('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  me: () => fetchApi('/api/v1/auth/me'),

  // Campaigns
  createCampaign: (data: { intent: string; name?: string }) =>
    fetchApi('/api/v1/campaigns', { method: 'POST', body: JSON.stringify(data) }),
  listCampaigns: (params?: { status?: string; limit?: number; offset?: number }) => {
    const q = new URLSearchParams(params as any).toString();
    return fetchApi(`/api/v1/campaigns${q ? '?' + q : ''}`);
  },
  getCampaign: (id: string) => fetchApi(`/api/v1/campaigns/${id}`),
  approveCampaign: (id: string) =>
    fetchApi(`/api/v1/campaigns/${id}/approve`, { method: 'POST', body: JSON.stringify({}) }),
  getCampaignStats: (id: string) => fetchApi(`/api/v1/campaigns/${id}/stats`),
  exportCampaign: (id: string) =>
    fetchApi(`/api/v1/campaigns/${id}/export`, { method: 'POST' }),

  // Customers
  listCustomers: (params?: Record<string, any>) => {
    const q = new URLSearchParams(Object.entries(params || {}).filter(([,v]) => v != null).map(([k,v]) => [k, String(v)])).toString();
    return fetchApi(`/api/v1/customers${q ? '?' + q : ''}`);
  },
  getCustomer: (id: string) => fetchApi(`/api/v1/customers/${id}`),
  getCustomerStats: () => fetchApi('/api/v1/customers/stats'),

  // Twins
  getTwin: (customerId: string) => fetchApi(`/api/v1/twins/${customerId}`),
  getTwinHistory: (customerId: string) => fetchApi(`/api/v1/twins/${customerId}/history`),

  // Insights
  listInsights: () => fetchApi('/api/v1/insights'),
  getInsight: (id: string) => fetchApi(`/api/v1/insights/${id}`),

  // XenoPilot
  xenopilotChat: (message: string, history: Array<{role: string; content: string}>) =>
    fetchApi('/api/v1/xenopilot/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_history: history })
    }),

  // AWS
  awsStatus: () => fetchApi('/api/v1/aws/status'),
};

export const SSE_BASE = API_BASE;
export { API_BASE };

