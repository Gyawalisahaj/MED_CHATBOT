import axios, { AxiosError } from 'axios'
import type { TokenResponse, ChatHistoryItem } from '@/types'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

const http = axios.create({ baseURL: BASE, timeout: 60000 })

// ── Attach access token to every request ─────────────────────────────────────
http.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── On 401, try token refresh once ───────────────────────────────────────────
http.interceptors.response.use(
  (res) => res,
  async (err: AxiosError) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE}/api/v1/auth/refresh`, {
            refresh_token: refresh,
          })
          localStorage.setItem('access_token', data.access_token)
          if (err.config) {
            err.config.headers.Authorization = `Bearer ${data.access_token}`
            return http(err.config)
          }
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      } else {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

// ── Error message extractor ───────────────────────────────────────────────────
export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail?.message) {
      const errors = (detail.errors as string[]) || []
      return [detail.message, ...errors].join('\n')
    }
    if (Array.isArray(detail)) {
      return detail.map((d: { msg: string }) => d.msg).join('\n')
    }
  }
  return 'Something went wrong. Please try again.'
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => http.post<TokenResponse>('/api/v1/auth/register', data),

  login: (data: { identifier: string; password: string }) =>
    http.post<TokenResponse>('/api/v1/auth/login', data),

  googleLogin: (id_token: string) =>
    http.post<TokenResponse>('/api/v1/auth/google', { id_token }),

  me: () => http.get('/api/v1/auth/me'),

  logout: () => http.post('/api/v1/auth/logout'),
}

// ── Chat ──────────────────────────────────────────────────────────────────────
export const chatApi = {
  send: (message: string, session_id: string) =>
    http.post<{ answer: string; sources: string[]; session_id: string }>(
      '/api/v1/chat/query',
      { message, session_id }
    ),

  history: (session_id: string) =>
    http.get<ChatHistoryItem[]>(`/api/v1/chat/history/${session_id}`),

  clearHistory: (session_id: string) =>
    http.delete(`/api/v1/chat/history/${session_id}`),

  health: () => http.get('/api/v1/chat/health'),
}
