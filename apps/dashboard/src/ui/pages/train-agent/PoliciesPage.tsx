/** Policies – cancellations, payment terms, and procedures. */

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { organizationService } from '@/application/organization/organizationService'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'
import { FileText } from 'lucide-react'

export interface PolicyItem {
  title: string
  content: string
}

function getPolicies(settings: Record<string, unknown> | null | undefined): PolicyItem[] {
  const raw = settings?.policies
  if (!Array.isArray(raw)) return []
  return raw
    .filter((p): p is Record<string, unknown> => p && typeof p === 'object')
    .map((p) => ({
      title: (p.title ?? p.name ?? '') as string,
      content: (p.content ?? p.body ?? p.text ?? '') as string,
    }))
    .filter((p) => p.title.trim() || p.content.trim())
}

export function PoliciesPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''

  const { data: orgData } = useQuery({
    queryKey: ['organization', orgId],
    queryFn: () => organizationService.getOrganization(orgId),
    enabled: !!orgId,
  })

  const org = (orgData ?? currentOrganization) as {
    settings?: Record<string, unknown> | null
  } | null
  const policies = getPolicies(org?.settings ?? null)

  const [modalOpen, setModalOpen] = useState(false)
  const [editIndex, setEditIndex] = useState<number | null>(null)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  const updateOrg = useMutation({
    mutationFn: async (newPolicies: PolicyItem[]) => {
      if (!currentOrganization) throw new Error('No organization')
      const settings = (org?.settings ?? {}) as Record<string, unknown>
      return organizationService.updateOrganization(currentOrganization.id, {
        settings: { ...settings, policies: newPolicies },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      queryClient.invalidateQueries({ queryKey: ['organization', currentOrganization?.id] })
      setModalOpen(false)
      setEditIndex(null)
      setTitle('')
      setContent('')
    },
  })

  const openAdd = () => {
    setEditIndex(null)
    setTitle('')
    setContent('')
    setModalOpen(true)
  }

  const openEdit = (index: number) => {
    const p = policies[index]
    setEditIndex(index)
    setTitle(p.title)
    setContent(p.content)
    setModalOpen(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() && !content.trim()) return
    const newPolicies =
      editIndex !== null
        ? policies.map((p, i) => (i === editIndex ? { title: title.trim(), content: content.trim() } : p))
        : [...policies, { title: title.trim(), content: content.trim() }]
    updateOrg.mutate(newPolicies)
  }

  const handleDelete = (index: number) => {
    if (!window.confirm('Delete this policy?')) return
    const newPolicies = policies.filter((_, i) => i !== index)
    updateOrg.mutate(newPolicies)
  }

  if (!currentOrganization) {
    return (
      <div className="text-slate-600 dark:text-slate-400">
        Select an organization to configure policies.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Policies</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Configure cancellations, payment terms, and procedures your agent can communicate.
          </p>
        </div>
        <Button variant="accent" onClick={openAdd}>
          Add Policy
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Business Policies
          </CardTitle>
        </CardHeader>
        <CardContent>
          {policies.length === 0 ? (
            <p className="text-sm text-slate-500">
              No policies yet. Add cancellation, payment, or other policies your agent can reference.
            </p>
          ) : (
            <ul className="space-y-3">
              {policies.map((p, i) => (
                <li
                  key={i}
                  className="flex flex-col gap-2 rounded-lg border border-slate-200 p-4 dark:border-slate-700"
                >
                  <div>
                    <span className="text-xs font-medium text-slate-500">Title</span>
                    <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{p.title || '—'}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-500">Content</span>
                    <p className="whitespace-pre-wrap text-sm text-slate-600 dark:text-slate-300">
                      {p.content || '—'}
                    </p>
                  </div>
                  <div className="flex gap-2 pt-1">
                    <Button variant="ghost" size="sm" onClick={() => openEdit(i)}>
                      Edit
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-600" onClick={() => handleDelete(i)}>
                      Delete
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editIndex !== null ? 'Edit Policy' : 'Add Policy'}
        size="lg"
      >
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Title</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Cancellation Policy"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Content</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="e.g. Cancellations must be made at least 24 hours in advance. Late cancellations may incur a fee."
              rows={5}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={updateOrg.isPending}>
              {editIndex !== null ? 'Save' : 'Add'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
