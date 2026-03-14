/** FAQs – common questions your agent can answer. */

import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { organizationService } from '@/application/organization/organizationService'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'
import { HelpCircle } from 'lucide-react'

export interface FaqItem {
  question: string
  answer: string
}

function getFaqs(settings: Record<string, unknown> | null | undefined): FaqItem[] {
  const raw = settings?.faqs
  if (!Array.isArray(raw)) return []
  return raw
    .filter((f): f is Record<string, unknown> => f && typeof f === 'object')
    .map((f) => ({
      question: (f.question ?? f.q ?? '') as string,
      answer: (f.answer ?? f.a ?? '') as string,
    }))
    .filter((f) => f.question.trim() || f.answer.trim())
}

export function FAQsPage() {
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
  const faqs = getFaqs(org?.settings ?? null)

  const [modalOpen, setModalOpen] = useState(false)
  const [editIndex, setEditIndex] = useState<number | null>(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')

  const updateOrg = useMutation({
    mutationFn: async (newFaqs: FaqItem[]) => {
      if (!currentOrganization) throw new Error('No organization')
      const settings = (org?.settings ?? {}) as Record<string, unknown>
      return organizationService.updateOrganization(currentOrganization.id, {
        settings: { ...settings, faqs: newFaqs },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      queryClient.invalidateQueries({ queryKey: ['organization', currentOrganization?.id] })
      setModalOpen(false)
      setEditIndex(null)
      setQuestion('')
      setAnswer('')
    },
  })

  const openAdd = () => {
    setEditIndex(null)
    setQuestion('')
    setAnswer('')
    setModalOpen(true)
  }

  const openEdit = (index: number) => {
    const f = faqs[index]
    setEditIndex(index)
    setQuestion(f.question)
    setAnswer(f.answer)
    setModalOpen(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim() && !answer.trim()) return
    const newFaqs =
      editIndex !== null
        ? faqs.map((f, i) => (i === editIndex ? { question: question.trim(), answer: answer.trim() } : f))
        : [...faqs, { question: question.trim(), answer: answer.trim() }]
    updateOrg.mutate(newFaqs)
  }

  const handleDelete = (index: number) => {
    if (!window.confirm('Delete this FAQ?')) return
    const newFaqs = faqs.filter((_, i) => i !== index)
    updateOrg.mutate(newFaqs)
  }

  if (!currentOrganization) {
    return (
      <div className="text-slate-600 dark:text-slate-400">
        Select an organization to configure FAQs.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">FAQs</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Add common questions your agent can answer during calls.
          </p>
        </div>
        <Button variant="accent" onClick={openAdd}>
          Add FAQ
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5" />
            Frequently Asked Questions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {faqs.length === 0 ? (
            <p className="text-sm text-slate-500">No FAQs yet. Add questions and answers your agent can use.</p>
          ) : (
            <ul className="space-y-3">
              {faqs.map((f, i) => (
                <li
                  key={i}
                  className="flex flex-col gap-2 rounded-lg border border-slate-200 p-4 dark:border-slate-700"
                >
                  <div>
                    <span className="text-xs font-medium text-slate-500">Question</span>
                    <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{f.question || '—'}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-500">Answer</span>
                    <p className="text-sm text-slate-600 dark:text-slate-300">{f.answer || '—'}</p>
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

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editIndex !== null ? 'Edit FAQ' : 'Add FAQ'}>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Question</label>
            <Input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. What are your opening hours?"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Answer</label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="e.g. We are open Monday to Friday, 9am–5pm."
              rows={4}
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
