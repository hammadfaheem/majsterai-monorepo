/** Departments – list and CRUD for org departments. */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

interface Department {
  id: number
  org_id: string
  name: string
  description: string | null
  default_schedule_id: number | null
  is_active: boolean
  max_concurrent_calls: number | null
  escalation_timeout: number | null
  escalation_settings: Record<string, unknown> | null
  created_at: number
  updated_at: number
}

interface Schedule {
  id: number
  name: string
  time_zone: string
  department_id: number | null
}

export function DepartmentsPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''
  const [modalOpen, setModalOpen] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [defaultScheduleId, setDefaultScheduleId] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [maxConcurrentCalls, setMaxConcurrentCalls] = useState('')
  const [escalationTimeout, setEscalationTimeout] = useState('')

  const { data: departments = [] } = useQuery({
    queryKey: ['departments', orgId],
    queryFn: async () => {
      const res = await apiClient.get<Department[]>(`/api/departments/org/${orgId}`)
      return res.data
    },
    enabled: !!orgId,
  })

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      const res = await apiClient.get<Schedule[]>('/api/schedules/')
      return res.data
    },
    enabled: modalOpen,
  })

  const createDepartment = useMutation({
    mutationFn: () =>
      apiClient.post<Department>('/api/departments/', {
        org_id: orgId,
        name,
        description: description || null,
        default_schedule_id: defaultScheduleId ? parseInt(defaultScheduleId, 10) : null,
        is_active: isActive,
        max_concurrent_calls: maxConcurrentCalls ? parseInt(maxConcurrentCalls, 10) : null,
        escalation_timeout: escalationTimeout ? parseInt(escalationTimeout, 10) : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments', orgId] })
      setModalOpen(false)
      setName('')
      setDescription('')
      setDefaultScheduleId('')
      setIsActive(true)
      setMaxConcurrentCalls('')
      setEscalationTimeout('')
      setEditId(null)
    },
  })

  const updateDepartment = useMutation({
    mutationFn: (id: number) =>
      apiClient.put<Department>(`/api/departments/${id}`, {
        name,
        description: description || null,
        default_schedule_id: defaultScheduleId ? parseInt(defaultScheduleId, 10) : null,
        is_active: isActive,
        max_concurrent_calls: maxConcurrentCalls ? parseInt(maxConcurrentCalls, 10) : null,
        escalation_timeout: escalationTimeout ? parseInt(escalationTimeout, 10) : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments', orgId] })
      setModalOpen(false)
      setEditId(null)
    },
  })

  const deleteDepartment = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/departments/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['departments', orgId] }),
  })

  const openAdd = () => {
    setEditId(null)
    setName('')
    setDescription('')
    setDefaultScheduleId('')
    setIsActive(true)
    setMaxConcurrentCalls('')
    setEscalationTimeout('')
    setModalOpen(true)
  }

  const openEdit = (d: Department) => {
    setEditId(d.id)
    setName(d.name)
    setDescription(d.description ?? '')
    setDefaultScheduleId(d.default_schedule_id != null ? String(d.default_schedule_id) : '')
    setIsActive(d.is_active)
    setMaxConcurrentCalls(d.max_concurrent_calls != null ? String(d.max_concurrent_calls) : '')
    setEscalationTimeout(d.escalation_timeout != null ? String(d.escalation_timeout) : '')
    setModalOpen(true)
  }

  const handleSubmit = () => {
    if (!name.trim()) return
    if (editId != null) updateDepartment.mutate(editId)
    else createDepartment.mutate()
  }

  const scheduleName = (scheduleId: number) => schedules.find((s) => s.id === scheduleId)?.name ?? scheduleId

  return (
    <div className="p-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Departments</CardTitle>
          <Button onClick={openAdd} disabled={!orgId}>
            Add department
          </Button>
        </CardHeader>
        <CardContent>
          {!orgId ? (
            <p className="text-muted-foreground">Select an organization first.</p>
          ) : departments.length === 0 ? (
            <p className="text-muted-foreground">No departments yet. Add one to get started.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Name</th>
                    <th className="text-left py-2">Description</th>
                    <th className="text-left py-2">Schedule</th>
                    <th className="text-left py-2">Active</th>
                    <th className="text-right py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map((d) => (
                    <tr key={d.id} className="border-b">
                      <td className="py-2">{d.name}</td>
                      <td className="py-2 max-w-[200px] truncate">{d.description ?? '—'}</td>
                      <td className="py-2">{d.default_schedule_id != null ? scheduleName(d.default_schedule_id) : '—'}</td>
                      <td className="py-2">{d.is_active ? 'Yes' : 'No'}</td>
                      <td className="py-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(d)}>
                          Edit
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteDepartment.mutate(d.id)}
                          disabled={deleteDepartment.isPending}
                        >
                          Delete
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

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editId != null ? 'Edit department' : 'Add department'}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Sales" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional" />
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
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
              <span className="text-sm">Active</span>
            </label>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Max concurrent calls</label>
            <Input
              type="number"
              value={maxConcurrentCalls}
              onChange={(e) => setMaxConcurrentCalls(e.target.value)}
              placeholder="Optional"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Escalation timeout (seconds)</label>
            <Input
              type="number"
              value={escalationTimeout}
              onChange={(e) => setEscalationTimeout(e.target.value)}
              placeholder="Optional"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!name.trim() || createDepartment.isPending || updateDepartment.isPending}
            >
              {editId != null ? 'Save' : 'Create'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
