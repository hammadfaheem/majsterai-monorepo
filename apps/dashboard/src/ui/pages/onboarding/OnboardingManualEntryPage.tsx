import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { setOnboardingData, getOnboardingData } from '@/application/onboarding/onboardingStore'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'

const COMMON_TIMEZONES = [
  'UTC',
  'Europe/Warsaw',
  'Europe/London',
  'Europe/Berlin',
  'America/New_York',
  'America/Los_Angeles',
  'Asia/Tokyo',
  'Australia/Sydney',
]

const COUNTRIES = [
  { code: 'AU', name: 'Australia' },
  { code: 'US', name: 'United States' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'PL', name: 'Poland' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'CA', name: 'Canada' },
  { code: 'NZ', name: 'New Zealand' },
  { code: 'JP', name: 'Japan' },
]

export function OnboardingManualEntryPage() {
  const saved = getOnboardingData()
  const [orgName, setOrgName] = useState(saved?.org_name ?? '')
  const [timeZone, setTimeZone] = useState(saved?.time_zone ?? 'UTC')
  const [country, setCountry] = useState(saved?.country ?? '')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!orgName.trim()) {
      setError('Organization name is required')
      return
    }
    setOnboardingData({
      org_name: orgName.trim(),
      time_zone: timeZone,
      country: country || undefined,
    })
    navigate('/onboarding/register-account', { replace: true })
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg dark:border-slate-700 dark:bg-slate-900">
      <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
        Set up your organization
      </h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
        Enter your business details. You can change these later in Settings.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
            {error}
          </div>
        )}
        <div>
          <label
            htmlFor="org_name"
            className="block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Organization name
          </label>
          <Input
            id="org_name"
            type="text"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            placeholder="My Company"
            className="mt-1"
            required
            autoFocus
          />
        </div>
        <div>
          <label
            htmlFor="time_zone"
            className="block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Time zone
          </label>
          <select
            id="time_zone"
            value={timeZone}
            onChange={(e) => setTimeZone(e.target.value)}
            className="mt-1 flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
          >
            {COMMON_TIMEZONES.map((tz) => (
              <option key={tz} value={tz}>
                {tz}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label
            htmlFor="country"
            className="block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Country (optional)
          </label>
          <select
            id="country"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            className="mt-1 flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
          >
            <option value="">Select country</option>
            {COUNTRIES.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <Button type="submit" variant="accent" className="w-full">
          Continue
        </Button>
      </form>
    </div>
  )
}
