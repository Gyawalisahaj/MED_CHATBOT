// ── Auth types ────────────────────────────────────────────────────────────────
export interface User {
    id: number
    username: string
    email: string
    full_name: string | null
    is_google_user: boolean
    picture: string | null
    is_active: boolean
    is_verified: boolean
    created_at: string
}

export interface TokenResponse {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
    user: User
}

// ── Chat types ────────────────────────────────────────────────────────────────
export interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    sources?: string[]
    timestamp: string
    isStreaming?: boolean
}

export interface Conversation {
    id: string
    title: string
    messages: Message[]
    createdAt: string
    updatedAt: string
}

export interface ChatHistoryItem {
    id: number
    session_id: string
    message: string
    response: string
    sources: string[]
    timestamp: string
}

export interface PasswordStrength {
    score: number
    label: string
    color: string
    checks: { label: string; passed: boolean }[]
}