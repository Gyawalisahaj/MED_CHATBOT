'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, Stethoscope, AlertCircle } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { authApi, getErrorMessage } from '@/lib/api'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

export default function LoginPage() {
    const { login, isAuthenticated } = useAuth()
    const router = useRouter()

    const [identifier, setIdentifier] = useState('')
    const [password, setPassword] = useState('')
    const [showPw, setShowPw] = useState(false)
    const [loading, setLoading] = useState(false)
    const [googleLoading, setGoogleLoading] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => { if (isAuthenticated) router.replace('/chat') }, [isAuthenticated, router])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        if (!identifier.trim() || !password) { setError('Please fill in all fields.'); return }
        setLoading(true)
        try {
            const { data } = await authApi.login({ identifier: identifier.trim(), password })
            login(data)
            router.push('/chat')
        } catch (err) {
            setError(getErrorMessage(err))
        } finally {
            setLoading(false)
        }
    }

    const handleGoogle = () => {
        // Google One Tap / Sign-In — requires NEXT_PUBLIC_GOOGLE_CLIENT_ID
        const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
        if (!clientId) { setError('Google Sign-In is not configured.'); return }
        // We use the implicit flow to get an id_token, then POST it to our backend
        const params = new URLSearchParams({
            client_id: clientId,
            redirect_uri: window.location.origin + '/auth/google/callback',
            response_type: 'id_token',
            scope: 'openid email profile',
            nonce: Math.random().toString(36).slice(2),
        })
        window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`
    }

    return (
        <div className="min-h-screen bg-surface flex items-center justify-center p-4">
            {/* Background mesh */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-teal/5 blur-3xl" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-teal/3 blur-3xl" />
            </div>

            <div className="relative w-full max-w-md animate-slide-up">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-2 mb-3">
                        <div className="w-9 h-9 rounded-xl bg-teal/20 flex items-center justify-center">
                            <Stethoscope size={20} className="text-teal" />
                        </div>
                        <span className="text-xl font-semibold text-ink">MediQuery AI</span>
                    </div>
                    <h1 className="text-2xl font-semibold text-ink">Welcome back</h1>
                    <p className="text-sm text-muted mt-1">Sign in to your account</p>
                </div>

                {/* Card */}
                <div className="bg-card border border-border rounded-2xl p-7 shadow-2xl shadow-black/40">
                    {/* Google button */}
                    <button
                        onClick={handleGoogle}
                        disabled={googleLoading}
                        className="w-full flex items-center justify-center gap-3 py-2.5 px-4 rounded-lg
                       border border-border bg-sidebar hover:bg-sidebar-hover text-sm font-medium
                       text-ink transition-colors duration-150 mb-5 disabled:opacity-50"
                    >
                        <svg width="18" height="18" viewBox="0 0 48 48">
                            <path fill="#FFC107" d="M43.6 20H24v8h11.3C33.7 33.1 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.7 1.1 7.8 2.9l5.7-5.7C34 6.5 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20c11.1 0 20-8.9 20-20 0-1.3-.1-2.7-.4-4z" />
                            <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.6 16 19 13 24 13c3 0 5.7 1.1 7.8 2.9l5.7-5.7C34 6.5 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
                            <path fill="#4CAF50" d="M24 44c5.2 0 9.9-1.9 13.5-5l-6.2-5.2C29.4 35.5 26.8 36 24 36c-5.2 0-9.7-3-11.7-7.5l-6.5 5C9.5 40.4 16.2 44 24 44z" />
                            <path fill="#1976D2" d="M43.6 20H24v8h11.3c-.9 2.5-2.6 4.6-4.8 6l6.2 5.2C40.3 35.9 44 30.4 44 24c0-1.3-.1-2.7-.4-4z" />
                        </svg>
                        Continue with Google
                    </button>

                    {/* Divider */}
                    <div className="flex items-center gap-3 mb-5">
                        <div className="flex-1 h-px bg-border" />
                        <span className="text-xs text-muted">or</span>
                        <div className="flex-1 h-px bg-border" />
                    </div>

                    {/* Error */}
                    {error && (
                        <div className="mb-4 flex gap-2 items-start p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                            <AlertCircle size={16} className="text-red-400 flex-shrink-0 mt-0.5" />
                            <p className="text-sm text-red-300 whitespace-pre-line">{error}</p>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <Input
                            label="Username or Email"
                            type="text"
                            placeholder="drgyawali or doctor@hospital.com"
                            value={identifier}
                            onChange={(e) => setIdentifier(e.target.value)}
                            autoComplete="username"
                            autoFocus
                        />
                        <Input
                            label="Password"
                            type={showPw ? 'text' : 'password'}
                            placeholder="Your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            autoComplete="current-password"
                            rightIcon={
                                <button
                                    type="button"
                                    onClick={() => setShowPw(!showPw)}
                                    className="hover:text-ink transition-colors"
                                >
                                    {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            }
                        />
                        <Button type="submit" fullWidth loading={loading} className="mt-2">
                            Sign in
                        </Button>
                    </form>

                    <p className="mt-5 text-center text-sm text-muted">
                        Don&apos;t have an account?{' '}
                        <Link href="/register" className="text-teal hover:text-teal-hover font-medium">
                            Create one
                        </Link>
                    </p>
                </div>

                <p className="text-center text-xs text-muted mt-5">
                    ⚠️ Educational use only. Not a substitute for professional medical advice.
                </p>
            </div>
        </div>
    )
}