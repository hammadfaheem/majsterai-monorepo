import { useState } from 'react'
import { createFileRoute, redirect, useRouter } from '@tanstack/react-router'
import { api } from '@/utils/api'
import { setAuth } from '@/utils/auth'
import type { LoginResponse } from '@/types/api'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/Card'
import { ShieldCheck } from 'lucide-react'

export const Route = createFileRoute('/')({
  beforeLoad: ({ context }) => {
    if (context.user?.role === 'SUPERADMIN') {
      throw redirect({ to: '/organizations' })
    }
  },
  component: LoginPage,
})

function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const { data } = await api.post<LoginResponse>('/api/auth/login', { email, password })
      if (data.user.role !== 'SUPERADMIN') {
        setError('Access denied. SUPERADMIN role required.')
        return
      }
      setAuth(data.access_token, data.user)
      await router.invalidate()
      void router.navigate({ to: '/organizations' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="flex flex-col items-center gap-2">
          <div className="flex items-center justify-center h-12 w-12 rounded-xl bg-[#142236]">
            <ShieldCheck className="h-6 w-6 text-primary-400" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">
            Majster<span className="text-accent">AI</span> Admin
          </h1>
          <p className="text-sm text-slate-500">SUPERADMIN access only</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Sign in</CardTitle>
            <CardDescription>Enter your credentials to access the admin panel.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-slate-700" htmlFor="email">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@example.com"
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-slate-700" htmlFor="password">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Signing in…' : 'Sign in'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
