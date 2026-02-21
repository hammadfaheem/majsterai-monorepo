/** Appointments – list and manage scheduled appointments. */

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { appointmentService } from '@/application/appointment/appointmentService'
import { leadService } from '@/application/lead/leadService'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'
import { FilterBar } from '@/ui/components/FilterBar'

interface TradeService {
  id: number
  name: string
}

export function AppointmentsPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [createTitle, setCreateTitle] = useState('')
  const [createStart, setCreateStart] = useState('')
  const [createEnd, setCreateEnd] = useState('')
  const [createLeadId, setCreateLeadId] = useState('')
  const [createServiceId, setCreateServiceId] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ['appointments', currentOrganization?.id],
    queryFn: () => appointmentService.list(currentOrganization?.id ?? '', { limit: 500 }),
    enabled: !!currentOrganization?.id,
  })

  const { data: leads = [] } = useQuery({
    queryKey: ['leads', currentOrganization?.id],
    queryFn: () => leadService.listLeads(currentOrganization?.id ?? '', { limit: 500 }),
    enabled: !!currentOrganization?.id && createOpen,
  })

  const { data: services = [] } = useQuery({
    queryKey: ['trade-services', currentOrganization?.id],
    queryFn: async () => {
      const { data } = await apiClient.get<TradeService[]>(
        `/api/trade-services/org/${currentOrganization?.id ?? ''}`
      )
      return data
    },
    enabled: !!currentOrganization?.id && createOpen,
  })

  const filteredAppointments = useMemo(() => {
    if (!statusFilter) return appointments
    return appointments.filter((a) => a.status === statusFilter)
  }, [appointments, statusFilter])

  const createAppointment = useMutation({
    mutationFn: async (payload: {
      org_id: string
      title: string
      start: number
      end: number
      lead_id?: string
      trade_service_id?: number
    }) => {
      const { data } = await apiClient.post('/api/appointments/', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments', currentOrganization?.id] })
      setCreateOpen(false)
      setCreateTitle('')
      setCreateStart('')
      setCreateEnd('')
      setCreateLeadId('')
      setCreateServiceId('')
    },
  })

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!currentOrganization?.id || !createStart || !createEnd) return
    const startMs = new Date(createStart).getTime()
    const endMs = new Date(createEnd).getTime()
    createAppointment.mutate({
      org_id: currentOrganization.id,
      title: createTitle || 'Appointment',
      start: startMs,
      end: endMs,
      lead_id: createLeadId || undefined,
      trade_service_id: createServiceId ? parseInt(createServiceId, 10) : undefined,
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Appointments</h1>
          <p className="mt-2 text-sm text-slate-600">
            View and manage scheduled appointments
          </p>
        </div>
        <Button variant="accent" onClick={() => setCreateOpen(true)}>
          Create appointment
        </Button>
      </div>

      <FilterBar
        searchValue=""
        onSearchChange={() => {}}
        searchPlaceholder="Filter appointments..."
        filterOptions={[
          {
            label: 'Status',
            value: statusFilter,
            options: [
              { value: '', label: 'All' },
              { value: 'scheduled', label: 'Scheduled' },
              { value: 'completed', label: 'Completed' },
              { value: 'cancelled', label: 'Cancelled' },
              { value: 'no_show', label: 'No show' },
            ],
            onChange: setStatusFilter,
          },
        ]}
      />

      <Card>
        <CardHeader>
          <CardTitle>Upcoming & past</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : filteredAppointments.length === 0 ? (
            <p className="text-sm text-slate-500">No appointments yet.</p>
          ) : (
            <ul className="space-y-2">
              {filteredAppointments.slice(0, 50).map((apt) => (
                <li key={apt.id} className="flex justify-between text-sm">
                  <span className="font-medium">{apt.title || 'Untitled'}</span>
                  <span className="text-slate-500">
                    {new Date(apt.start).toLocaleString()} – {apt.status}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="Create appointment">
        <form className="space-y-4" onSubmit={handleCreate}>
          <div>
            <label className="block text-sm font-medium text-slate-700">Title</label>
            <Input
              value={createTitle}
              onChange={(e) => setCreateTitle(e.target.value)}
              placeholder="Appointment title"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Lead</label>
            <select
              value={createLeadId}
              onChange={(e) => setCreateLeadId(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">None</option>
              {leads.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Service</label>
            <select
              value={createServiceId}
              onChange={(e) => setCreateServiceId(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">None</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Start (date & time)</label>
            <Input
              type="datetime-local"
              value={createStart}
              onChange={(e) => setCreateStart(e.target.value)}
              className="mt-1"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">End (date & time)</label>
            <Input
              type="datetime-local"
              value={createEnd}
              onChange={(e) => setCreateEnd(e.target.value)}
              className="mt-1"
              required
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={createAppointment.isPending}>
              {createAppointment.isPending ? 'Creating…' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
