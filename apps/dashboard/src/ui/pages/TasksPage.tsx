/** Tasks – list and manage tasks (filter by assignee/lead/complete). */

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { taskService } from '@/application/task/taskService'
import { leadService } from '@/application/lead/leadService'
import { membershipService } from '@/application/membership/membershipService'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

export function TasksPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''
  const [filterComplete, setFilterComplete] = useState<'all' | 'incomplete' | 'complete'>('incomplete')
  const [createOpen, setCreateOpen] = useState(false)
  const [createTitle, setCreateTitle] = useState('')
  const [createLeadId, setCreateLeadId] = useState('')
  const [createAssignedMemberId, setCreateAssignedMemberId] = useState('')

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['tasks', orgId],
    queryFn: () => taskService.listTasks(orgId),
    enabled: !!orgId,
  })

  const { data: leads = [] } = useQuery({
    queryKey: ['leads', orgId],
    queryFn: () => leadService.listLeads(orgId, { limit: 500 }),
    enabled: !!orgId && createOpen,
  })

  const { data: members = [] } = useQuery({
    queryKey: ['memberships', orgId],
    queryFn: () => membershipService.listMembers(orgId),
    enabled: !!orgId && createOpen,
  })

  const filteredTasks = useMemo(() => {
    if (filterComplete === 'all') return tasks
    if (filterComplete === 'complete') return tasks.filter((t) => t.is_completed)
    return tasks.filter((t) => !t.is_completed)
  }, [tasks, filterComplete])

  const createTask = useMutation({
    mutationFn: () =>
      taskService.createTask({
        org_id: orgId,
        title: createTitle,
        lead_id: createLeadId || undefined,
        assigned_member_id: createAssignedMemberId || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', orgId] })
      setCreateOpen(false)
      setCreateTitle('')
      setCreateLeadId('')
      setCreateAssignedMemberId('')
    },
  })

  const toggleComplete = useMutation({
    mutationFn: ({ taskId, is_completed }: { taskId: string; is_completed: boolean }) =>
      taskService.updateTask(taskId, { is_completed }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks', orgId] }),
  })

  const deleteTask = useMutation({
    mutationFn: (taskId: string) => taskService.deleteTask(taskId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks', orgId] }),
  })

  const handleCreate = () => {
    if (!createTitle.trim()) return
    createTask.mutate()
  }

  const leadById = (id: string | null) => (id ? leads.find((l) => l.id === id) : null)
  const memberById = (id: string | null) => (id ? members.find((m) => m.id === id) : null)

  return (
    <div className="p-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between flex-wrap gap-4">
          <CardTitle>Tasks</CardTitle>
          <div className="flex items-center gap-2 flex-wrap">
            <select
              className="border rounded px-3 py-2 text-sm"
              value={filterComplete}
              onChange={(e) => setFilterComplete(e.target.value as 'all' | 'incomplete' | 'complete')}
            >
              <option value="incomplete">To do</option>
              <option value="complete">Done</option>
              <option value="all">All</option>
            </select>
            <Button onClick={() => setCreateOpen(true)} disabled={!orgId}>
              Add task
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {!orgId ? (
            <p className="text-muted-foreground">Select an organization first.</p>
          ) : isLoading ? (
            <p className="text-muted-foreground">Loading tasks…</p>
          ) : filteredTasks.length === 0 ? (
            <p className="text-muted-foreground">No tasks match the filter.</p>
          ) : (
            <ul className="space-y-2">
              {filteredTasks.map((t) => (
                <li
                  key={t.id}
                  className="flex items-center justify-between gap-4 py-2 border-b border-border last:border-0"
                >
                  <label className="flex items-center gap-2 flex-1 min-w-0 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={t.is_completed}
                      onChange={() => toggleComplete.mutate({ taskId: t.id, is_completed: !t.is_completed })}
                      disabled={toggleComplete.isPending}
                    />
                    <span className={t.is_completed ? 'line-through text-muted-foreground' : ''}>{t.title}</span>
                  </label>
                  <span className="text-muted-foreground text-sm shrink-0">
                    {t.lead_id ? `Lead: ${leadById(t.lead_id)?.name ?? t.lead_id}` : ''}
                    {t.assigned_member_id
                      ? ` · ${memberById(t.assigned_member_id)?.user_id ?? t.assigned_member_id}`
                      : ''}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteTask.mutate(t.id)}
                    disabled={deleteTask.isPending}
                  >
                    Delete
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="Add task">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <Input value={createTitle} onChange={(e) => setCreateTitle(e.target.value)} placeholder="Task title" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Lead (optional)</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={createLeadId}
              onChange={(e) => setCreateLeadId(e.target.value)}
            >
              <option value="">None</option>
              {leads.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name ?? l.email ?? l.id}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Assign to (optional)</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={createAssignedMemberId}
              onChange={(e) => setCreateAssignedMemberId(e.target.value)}
            >
              <option value="">None</option>
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.user_id} {m.role ? `(${m.role})` : ''}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={!createTitle.trim() || createTask.isPending}>
              Create
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
