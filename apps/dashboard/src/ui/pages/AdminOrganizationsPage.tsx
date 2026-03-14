/** Platform admin – list and edit all organizations. */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminService } from '@/application/admin/adminService'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'
import type { AdminOrganization } from '@/application/admin/adminService'

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

interface Schedule {
  id: number
  name: string
  time_zone: string
  department_id: number | null
}

export function AdminOrganizationsPage() {
  const queryClient = useQueryClient()
  const [editId, setEditId] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [timeZone, setTimeZone] = useState('UTC')
  const [country, setCountry] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [defaultScheduleId, setDefaultScheduleId] = useState('')
  const [tag, setTag] = useState('')
  const [seats, setSeats] = useState('')

  const { data: organizations = [], isLoading, isError, error } = useQuery({
    queryKey: ['admin-organizations'],
    queryFn: () => adminService.listOrganizations(),
  })

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      const { data } = await apiClient.get<Schedule[]>('/api/schedules/')
      return data
    },
    enabled: !!editId,
  })

  const updateOrg = useMutation({
    mutationFn: (orgId: string) =>
      adminService.updateOrganization(orgId, {
        name: name || undefined,
        time_zone: timeZone || undefined,
        country: country || undefined,
        currency: currency || undefined,
        default_schedule_id: defaultScheduleId ? parseInt(defaultScheduleId, 10) : undefined,
        tag: tag || undefined,
        seats: seats ? parseInt(seats, 10) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-organizations'] })
      setEditId(null)
    },
  })

  const openEdit = (org: AdminOrganization) => {
    setEditId(org.id)
    setName(org.name)
    setTimeZone(org.time_zone ?? 'UTC')
    setCountry(org.country ?? '')
    setCurrency(org.currency ?? 'USD')
    setDefaultScheduleId(org.default_schedule_id != null ? String(org.default_schedule_id) : '')
    setTag(org.tag ?? '')
    setSeats(org.seats != null ? String(org.seats) : '')
  }

  const handleSave = () => {
    if (editId) updateOrg.mutate(editId)
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Platform Admin – Organizations</h1>
        <p className="mt-2 text-sm text-slate-600">View and edit all organizations (superadmin only).</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All organizations</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : isError ? (
            <p className="text-sm text-red-600">{error instanceof Error ? error.message : 'Failed to load'}</p>
          ) : organizations.length === 0 ? (
            <p className="text-sm text-slate-500">No organizations.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Name</th>
                    <th className="text-left py-2">Slug</th>
                    <th className="text-left py-2">Time zone</th>
                    <th className="text-left py-2">Country</th>
                    <th className="text-right py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {organizations.map((org) => (
                    <tr key={org.id} className="border-b">
                      <td className="py-2">{org.name}</td>
                      <td className="py-2">{org.slug}</td>
                      <td className="py-2">{org.time_zone}</td>
                      <td className="py-2">{org.country ?? '—'}</td>
                      <td className="py-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(org)}>
                          Edit
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Modal open={!!editId} onClose={() => setEditId(null)} title="Edit organization">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Time zone</label>
            <Input value={timeZone} onChange={(e) => setTimeZone(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Country</label>
            <select
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="w-full border rounded px-3 py-2"
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
            <label className="block text-sm font-medium mb-1">Currency</label>
            <Input value={currency} onChange={(e) => setCurrency(e.target.value)} placeholder="USD, EUR" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Default schedule</label>
            <select
              className="w-full border rounded px-3 py-2"
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
            <label className="block text-sm font-medium mb-1">Tag</label>
            <Input value={tag} onChange={(e) => setTag(e.target.value)} placeholder="Optional" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Seats</label>
            <Input type="number" value={seats} onChange={(e) => setSeats(e.target.value)} placeholder="Optional" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setEditId(null)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={updateOrg.isPending}>
              Save
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
