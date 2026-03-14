/** Settings page – org settings and preferences. */

import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { organizationService } from '@/application/organization/organizationService'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'

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

export function SettingsPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [timeZone, setTimeZone] = useState('UTC')
  const [country, setCountry] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [defaultScheduleId, setDefaultScheduleId] = useState<string>('')
  const [tag, setTag] = useState('')
  const [seats, setSeats] = useState<string>('')

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ id: number; name: string; time_zone: string }[]>('/api/schedules/')
      return data
    },
  })

  useEffect(() => {
    if (currentOrganization) {
      setName(currentOrganization.name)
      setTimeZone((currentOrganization as { time_zone?: string }).time_zone ?? 'UTC')
      setCountry((currentOrganization as { country?: string | null }).country ?? '')
      setCurrency((currentOrganization as { currency?: string }).currency ?? 'USD')
      const ds = (currentOrganization as { default_schedule_id?: number | null }).default_schedule_id
      setDefaultScheduleId(ds != null ? String(ds) : '')
      setTag((currentOrganization as { tag?: string | null }).tag ?? '')
      setSeats(
        (currentOrganization as { seats?: number | null }).seats != null
          ? String((currentOrganization as { seats?: number | null }).seats)
          : ''
      )
    }
  }, [currentOrganization])

  const updateOrg = useMutation({
    mutationFn: () =>
      organizationService.updateOrganization(currentOrganization!.id, {
        name: name || undefined,
        time_zone: timeZone || undefined,
        country: country || undefined,
        currency: currency || undefined,
        default_schedule_id: defaultScheduleId ? parseInt(defaultScheduleId, 10) : undefined,
        tag: tag || undefined,
        seats: seats ? parseInt(seats, 10) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      queryClient.invalidateQueries({ queryKey: ['organization', currentOrganization?.id] })
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Settings</h1>
        <p className="mt-2 text-sm text-slate-600">
          Organization and preferences
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Organization</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700">Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Organization name"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Time zone</label>
            <Input
              value={timeZone}
              onChange={(e) => setTimeZone(e.target.value)}
              placeholder="e.g. UTC, Europe/Warsaw"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Country</label>
            <select
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
          <div>
            <label className="block text-sm font-medium text-slate-700">Currency</label>
            <Input
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              placeholder="e.g. USD, EUR, PLN"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Default schedule</label>
            <select
              className="mt-1 w-full border rounded px-3 py-2"
              value={defaultScheduleId}
              onChange={(e) => setDefaultScheduleId(e.target.value)}
            >
              <option value="">None</option>
              {schedules.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.time_zone})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Tag</label>
            <Input
              value={tag}
              onChange={(e) => setTag(e.target.value)}
              placeholder="e.g. DEMO, LIVE"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Seats</label>
            <Input
              type="number"
              value={seats}
              onChange={(e) => setSeats(e.target.value)}
              placeholder="Optional"
              className="mt-1"
            />
          </div>
          <Button
            variant="accent"
            onClick={() => updateOrg.mutate()}
            disabled={updateOrg.isPending}
          >
            {updateOrg.isPending ? 'Saving…' : 'Save'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
