'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/authcontext'
import { authApi, getErrorMessage } from '@/lib/api'

export default function GoogleCallbackPage() {
  const router    = useRouter()
  const { login } = useAuth()
  const [error, setError] = useState('')

  useEffect(() => {
    const hash   = window.location.hash
    const params = new URLSearchParams(hash.replace('#', ''))
    let idToken  = params.get('id_token')

    if (!idToken) {
      const qp = new URLSearchParams(window.location.search)
      idToken   = qp.get('id_token')
    }

    if (!idToken) {
      setError('No Google token received. Please try again.')
      return
    }

    authApi.googleLogin(idToken)
      .then(({ data }) => {
        login(data)
        router.replace('/chat')
      })
      .catch((err) => {
        setError(getErrorMessage(err))
      })
  }, []) // eslint-disable-line

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <div className="text-center space-y-4">
        {error ? (
          <>
            <p className="text-red-400 text-sm max-w-xs">{error}</p>
            <button
              onClick={() => router.push('/login')}
              className="text-teal text-sm hover:underline"
            >
              Back to login
            </button>
          </>
        ) : (
          <>
            <div className="w-6 h-6 border-2 border-teal border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm text-muted">Signing you in with Google…</p>
          </>
        )}
      </div>
    </div>
  )
}
