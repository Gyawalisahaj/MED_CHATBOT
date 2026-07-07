'use client'
import React, { createContext, useContext, useEffect, useState } from 'react'
import type { User, TokenResponse } from '@/types'

interface AuthContextValue {
    user: User | null
    isLoading: boolean
    isAuthenticated: boolean
    login: (data: TokenResponse) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextValue>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    login: () => { },
    logout: () => { },
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        try {
            const stored = localStorage.getItem('user')
            const token = localStorage.getItem('access_token')
            if (stored && token) setUser(JSON.parse(stored))
        } catch {
            localStorage.clear()
        } finally {
            setIsLoading(false)
        }
    }, [])

    const login = (data: TokenResponse) => {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        setUser(data.user)
    }

    const logout = () => {
        localStorage.clear()
        setUser(null)
        window.location.href = '/login'
    }

    return (
        <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)