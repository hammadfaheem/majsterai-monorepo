/** Lead detail page – profile, timeline (notes + activities), tasks. */

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { leadService } from '@/application/lead/leadService'
import { taskService } from '@/application/task/taskService'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'
import { StatusBadge } from '@/ui/components/StatusBadge'

export function LeadDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const [noteModalOpen, setNoteModalOpen] = useState(false)
  const [activityModalOpen, setActivityModalOpen] = useState(false)
  const [taskModalOpen, setTaskModalOpen] = useState(false)
  const [noteContent, setNoteContent] = useState('')
  const [activityType, setActivityType] = useState('call')
  const [activityDesc, setActivityDesc] = useState('')
  const [taskTitle, setTaskTitle] = useState('')
  const [editLeadOpen, setEditLeadOpen] = useState(false)
  const [editName, setEditName] = useState('')
  const [editEmail, setEditEmail] = useState('')
  const [editPhone, setEditPhone] = useState('')
  const [editStatus, setEditStatus] = useState('')
  const [editSource, setEditSource] = useState('')

  const leadId = id ?? ''

  const { data: lead, isLoading: leadLoading } = useQuery({
    queryKey: ['lead', leadId],
    queryFn: () => leadService.getLead(leadId),
    enabled: !!leadId,
  })

  const { data: notes = [] } = useQuery({
    queryKey: ['lead-notes', leadId],
    queryFn: () => leadService.listNotes(leadId),
    enabled: !!leadId,
  })

  const { data: activities = [] } = useQuery({
    queryKey: ['lead-activities', leadId],
    queryFn: () => leadService.listActivities(leadId),
    enabled: !!leadId,
  })

  const { data: tasks = [] } = useQuery({
    queryKey: ['tasks', currentOrganization?.id, leadId],
    queryFn: () =>
      taskService.listTasks(currentOrganization?.id ?? '', { lead_id: leadId }),
    enabled: !!currentOrganization?.id && !!leadId,
  })

  const addNote = useMutation({
    mutationFn: () => leadService.addNote(leadId, { content: noteContent }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead-notes', leadId] })
      setNoteModalOpen(false)
      setNoteContent('')
    },
  })

  const addActivity = useMutation({
    mutationFn: () =>
      leadService.addActivity(leadId, { type: activityType, description: activityDesc }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead-activities', leadId] })
      setActivityModalOpen(false)
      setActivityType('call')
      setActivityDesc('')
    },
  })

  const addTask = useMutation({
    mutationFn: () =>
      taskService.createTask({
        org_id: currentOrganization!.id,
        title: taskTitle,
        lead_id: leadId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', currentOrganization?.id, leadId] })
      setTaskModalOpen(false)
      setTaskTitle('')
    },
  })

  const toggleTask = useMutation({
    mutationFn: ({ taskId, is_completed }: { taskId: string; is_completed: boolean }) =>
      taskService.updateTask(taskId, { is_completed }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', currentOrganization?.id, leadId] })
    },
  })

  const updateLead = useMutation({
    mutationFn: () =>
      leadService.updateLead(leadId, {
        name: editName || undefined,
        email: editEmail || undefined,
        phone: editPhone || undefined,
        status: editStatus || undefined,
        source: editSource || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead', leadId] })
      setEditLeadOpen(false)
    },
  })

  const openEdit = () => {
    if (lead) {
      setEditName(lead.name)
      setEditEmail(lead.email ?? '')
      setEditPhone(lead.phone ?? '')
      setEditStatus(lead.status)
      setEditSource(lead.source ?? '')
      setEditLeadOpen(true)
    }
  }

  const formatTs = (ms: number) => {
    const d = new Date(ms)
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (leadLoading || !lead) {
    return (
      <div className="p-6">
        {leadLoading ? (
          <p className="text-sm text-slate-500">Loading lead…</p>
        ) : (
          <p className="text-sm text-slate-500">Lead not found.</p>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => navigate('/leads')}>
          Back to leads
        </Button>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Lead</CardTitle>
          <Button variant="outline" onClick={openEdit}>
            Edit
          </Button>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="font-medium text-slate-900 dark:text-slate-100">{lead.name}</p>
          <p className="text-sm text-slate-600">{lead.email ?? '—'}</p>
          <p className="text-sm text-slate-600">{lead.phone ?? '—'}</p>
          <div className="flex items-center gap-2">
            <StatusBadge status={lead.status} />
            {lead.source && (
              <span className="text-sm text-slate-500">Source: {lead.source}</span>
            )}
          </div>
          {lead.last_contact_date && (
            <p className="text-xs text-slate-400">
              Last contact: {formatTs(lead.last_contact_date)}
            </p>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Notes</CardTitle>
            <Button variant="accent" onClick={() => setNoteModalOpen(true)}>
              Add note
            </Button>
          </CardHeader>
          <CardContent>
            {notes.length === 0 ? (
              <p className="text-sm text-slate-500">No notes yet.</p>
            ) : (
              <ul className="space-y-3">
                {notes.map((n) => (
                  <li key={n.id} className="border-l-2 border-slate-200 pl-3 text-sm">
                    <p className="text-slate-700">{n.content}</p>
                    <p className="text-xs text-slate-400">{formatTs(n.created_at)}</p>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Activity</CardTitle>
            <Button variant="accent" onClick={() => setActivityModalOpen(true)}>
              Log activity
            </Button>
          </CardHeader>
          <CardContent>
            {activities.length === 0 ? (
              <p className="text-sm text-slate-500">No activity yet.</p>
            ) : (
              <ul className="space-y-3">
                {activities.map((a) => (
                  <li key={a.id} className="border-l-2 border-slate-200 pl-3 text-sm">
                    <span className="font-medium text-slate-700">{a.type}</span>
                    <p className="text-slate-600">{a.description}</p>
                    <p className="text-xs text-slate-400">{formatTs(a.created_at)}</p>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Tasks</CardTitle>
          <Button variant="accent" onClick={() => setTaskModalOpen(true)}>
            Add task
          </Button>
        </CardHeader>
        <CardContent>
          {tasks.length === 0 ? (
            <p className="text-sm text-slate-500">No tasks for this lead.</p>
          ) : (
            <ul className="space-y-2">
              {tasks.map((t) => (
                <li key={t.id} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={t.is_completed}
                    onChange={() =>
                      toggleTask.mutate({
                        taskId: t.id,
                        is_completed: !t.is_completed,
                      })
                    }
                    className="rounded border-slate-300"
                  />
                  <span
                    className={
                      t.is_completed ? 'text-slate-400 line-through' : 'text-slate-700'
                    }
                  >
                    {t.title}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Modal open={noteModalOpen} onClose={() => setNoteModalOpen(false)} title="Add note">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            addNote.mutate()
          }}
        >
          <div>
            <label className="block text-sm font-medium text-slate-700">Content</label>
            <Input
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
              placeholder="Note content"
              className="mt-1"
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setNoteModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={addNote.isPending}>
              Add
            </Button>
          </div>
        </form>
      </Modal>

      <Modal open={activityModalOpen} onClose={() => setActivityModalOpen(false)} title="Log activity">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            addActivity.mutate()
          }}
        >
          <div>
            <label className="block text-sm font-medium text-slate-700">Type</label>
            <select
              value={activityType}
              onChange={(e) => setActivityType(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="call">Call</option>
              <option value="email">Email</option>
              <option value="meeting">Meeting</option>
              <option value="note">Note</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Description</label>
            <Input
              value={activityDesc}
              onChange={(e) => setActivityDesc(e.target.value)}
              placeholder="What happened?"
              className="mt-1"
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setActivityModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={addActivity.isPending}>
              Log
            </Button>
          </div>
        </form>
      </Modal>

      <Modal open={taskModalOpen} onClose={() => setTaskModalOpen(false)} title="Add task">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            addTask.mutate()
          }}
        >
          <div>
            <label className="block text-sm font-medium text-slate-700">Title</label>
            <Input
              value={taskTitle}
              onChange={(e) => setTaskTitle(e.target.value)}
              placeholder="Task title"
              className="mt-1"
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setTaskModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={addTask.isPending}>
              Add task
            </Button>
          </div>
        </form>
      </Modal>

      <Modal open={editLeadOpen} onClose={() => setEditLeadOpen(false)} title="Edit lead">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            updateLead.mutate()
          }}
        >
          <div>
            <label className="block text-sm font-medium text-slate-700">Name</label>
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="mt-1"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Email</label>
            <Input
              type="email"
              value={editEmail}
              onChange={(e) => setEditEmail(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Phone</label>
            <Input
              value={editPhone}
              onChange={(e) => setEditPhone(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Status</label>
            <select
              value={editStatus}
              onChange={(e) => setEditStatus(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="qualified">Qualified</option>
              <option value="converted">Converted</option>
              <option value="lost">Lost</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Source</label>
            <Input
              value={editSource}
              onChange={(e) => setEditSource(e.target.value)}
              className="mt-1"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setEditLeadOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={updateLead.isPending}>
              Save
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
