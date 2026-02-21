/** Schedules – list and CRUD for working schedules. */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

interface Schedule {
  id: number
  name: string
  time_zone: string
  department_id: number | null
}

export function SchedulesPage() {
  const queryClient = useQueryClient()
  const [modalOpen, setModalOpen] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [name, setName] = useState('')
  const [timeZone, setTimeZone] = useState('UTC')
  const [departmentId, setDepartmentId] = useState<string>('')

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      const { data } = await apiClient.get<Schedule[]>('/api/schedules/')
      return data
    },
  })

  const createSchedule = useMutation({
    mutationFn: () =>
      apiClient.post<Schedule>('/api/schedules/', {
        name,
        time_zone: timeZone,
        department_id: departmentId ? parseInt(departmentId, 10) : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      setModalOpen(false)
      setName('')
      setTimeZone('UTC')
      setDepartmentId('')
      setEditId(null)
    },
  })

  const updateSchedule = useMutation({
    mutationFn: (id: number) =>
      apiClient.put<Schedule>(`/api/schedules/${id}`, {
        name,
        time_zone: timeZone,
        department_id: departmentId ? parseInt(departmentId, 10) : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      setModalOpen(false)
      setEditId(null)
    },
  })

  const deleteSchedule = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/schedules/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['schedules'] }),
  })

  const openAdd = () => {
    setEditId(null)
    setName('')
    setTimeZone('UTC')
    setDepartmentId('')
    setModalOpen(true)
  }

  const openEdit = (s: Schedule) => {
    setEditId(s.id)
    setName(s.name)
    setTimeZone(s.time_zone)
    setDepartmentId(s.department_id != null ? String(s.department_id) : '')
    setModalOpen(true)
  }

  const handleSubmit = () => {
    if (!name.trim()) return
    if (editId != null) updateSchedule.mutate(editId)
    else createSchedule.mutate()
  }

  return (
    <div className="p-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Schedules</CardTitle>
          <Button onClick={openAdd}>Add schedule</Button>
        </CardHeader>
        <CardContent>
          {schedules.length === 0 ? (
            <p className="text-muted-foreground">No schedules yet. Add one to get started.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Name</th>
                    <th className="text-left py-2">Time zone</th>
                    <th className="text-left py-2">Department ID</th>
                    <th className="text-right py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {schedules.map((s) => (
                    <tr key={s.id} className="border-b">
                      <td className="py-2">{s.name}</td>
                      <td className="py-2">{s.time_zone}</td>
                      <td className="py-2">{s.department_id ?? '—'}</td>
                      <td className="py-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(s)}>
                          Edit
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteSchedule.mutate(s.id)}
                          disabled={deleteSchedule.isPending}
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
        title={editId != null ? 'Edit schedule' : 'Add schedule'}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Main" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Time zone</label>
            <Input value={timeZone} onChange={(e) => setTimeZone(e.target.value)} placeholder="UTC" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Department ID (optional)</label>
            <Input
              value={departmentId}
              onChange={(e) => setDepartmentId(e.target.value)}
              placeholder="Leave empty if none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={!name.trim() || createSchedule.isPending || updateSchedule.isPending}>
              {editId != null ? 'Save' : 'Create'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
