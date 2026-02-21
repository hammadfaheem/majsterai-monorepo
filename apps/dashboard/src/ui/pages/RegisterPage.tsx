import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAppDispatch } from '@/store/hooks'
import { setCredentials } from '@/store/authSlice'
import { userService } from '@/application/user/userService'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'

export function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await userService.register({ name, email, password })
      dispatch(setCredentials({ token: res.access_token, user: res.user }))
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col md:flex-row">
      {/* Branding block - left on desktop, top on mobile */}
      <div className="flex flex-col justify-center px-6 py-12 md:flex-1 md:px-12 md:py-16 bg-gradient-to-br from-primary-600 to-accent text-white">
        <h1 className="font-bold text-3xl tracking-tight md:text-4xl" style={{ fontFamily: 'Poppins, sans-serif' }}>
          Majster<span className="text-white/90">AI</span>
        </h1>
        <p className="mt-3 text-white/90 text-sm md:text-base max-w-sm">
          Voice AI Agent Platform — Build, test, and deploy intelligent voice assistants.
        </p>
        <span className="mt-6 inline-flex items-center rounded-full bg-white/20 px-3 py-1 text-xs font-medium backdrop-blur">
          Voice AI · CRM
        </span>
      </div>

      {/* Form - right on desktop, below on mobile */}
      <div className="flex flex-1 items-center justify-center px-4 py-8 md:py-12 md:px-8">
        <div className="w-full max-w-[400px] rounded-2xl border border-slate-200 bg-white p-8 shadow-lg dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Create an account</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Enter your name, email and password</p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            {error && (
              <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
                {error}
              </div>
            )}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                Name
              </label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                className="mt-1"
                required
                autoComplete="name"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="mt-1"
                required
                autoComplete="email"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1"
                required
                autoComplete="new-password"
              />
            </div>
            <Button type="submit" variant="accent" className="w-full" disabled={loading}>
              {loading ? 'Creating account…' : 'Register'}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-600 dark:text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-accent hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
