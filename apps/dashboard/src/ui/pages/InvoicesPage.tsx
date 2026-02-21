/** Invoices – list with filters, create, view/edit (no payment). */

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { leadService } from '@/application/lead/leadService'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

interface Invoice {
  id: string
  org_id: string
  lead_id: string | null
  index: number | null
  status: string
  date: number | null
  due_date: number | null
  tax_type: string | null
  reference: string | null
  notes: string | null
  created_at: number
  updated_at: number
}

export function InvoicesPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [createOpen, setCreateOpen] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [leadId, setLeadId] = useState('')
  const [status, setStatus] = useState('draft')
  const [date, setDate] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [reference, setReference] = useState('')
  const [notes, setNotes] = useState('')

  const { data: invoices = [], isLoading } = useQuery({
    queryKey: ['invoices', orgId],
    queryFn: async () => {
      const { data } = await apiClient.get<Invoice[]>('/api/invoices/', {
        params: { org_id: orgId, limit: 500 },
      })
      return data
    },
    enabled: !!orgId,
  })

  const { data: leads = [] } = useQuery({
    queryKey: ['leads', orgId],
    queryFn: () => leadService.listLeads(orgId, { limit: 500 }),
    enabled: !!orgId && (createOpen || editId != null),
  })

  const filteredInvoices = useMemo(() => {
    if (!statusFilter) return invoices
    return invoices.filter((i) => i.status === statusFilter)
  }, [invoices, statusFilter])

  const createInvoice = useMutation({
    mutationFn: () =>
      apiClient.post<Invoice>('/api/invoices/', {
        org_id: orgId,
        lead_id: leadId || null,
        status: status || 'draft',
        date: date ? new Date(date).getTime() : null,
        due_date: dueDate ? new Date(dueDate).getTime() : null,
        reference: reference || null,
        notes: notes || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices', orgId] })
      setCreateOpen(false)
      resetForm()
    },
  })

  const updateInvoice = useMutation({
    mutationFn: (id: string) =>
      apiClient.put<Invoice>(`/api/invoices/${id}`, {
        status,
        date: date ? new Date(date).getTime() : null,
        due_date: dueDate ? new Date(dueDate).getTime() : null,
        reference: reference || null,
        notes: notes || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices', orgId] })
      setEditId(null)
      resetForm()
    },
  })

  const deleteInvoice = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/invoices/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['invoices', orgId] }),
  })

  function resetForm() {
    setLeadId('')
    setStatus('draft')
    setDate('')
    setDueDate('')
    setReference('')
    setNotes('')
    setEditId(null)
  }

  const openCreate = () => {
    resetForm()
    setCreateOpen(true)
  }

  const openEdit = (inv: Invoice) => {
    setEditId(inv.id)
    setLeadId(inv.lead_id ?? '')
    setStatus(inv.status)
    setDate(inv.date ? new Date(inv.date).toISOString().slice(0, 10) : '')
    setDueDate(inv.due_date ? new Date(inv.due_date).toISOString().slice(0, 10) : '')
    setReference(inv.reference ?? '')
    setNotes(inv.notes ?? '')
  }

  const handleCreate = () => {
    createInvoice.mutate()
  }

  const handleUpdate = () => {
    if (editId) updateInvoice.mutate(editId)
  }

  const leadName = (id: string | null) => (id ? leads.find((l) => l.id === id)?.name ?? id : '—')

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Invoices</h1>
        <p className="mt-2 text-sm text-slate-600">View and manage invoices (no payment capture)</p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between flex-wrap gap-4">
          <CardTitle>All invoices</CardTitle>
          <div className="flex items-center gap-2 flex-wrap">
            <select
              className="border rounded px-3 py-2 text-sm"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All statuses</option>
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="paid">Paid</option>
              <option value="overdue">Overdue</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <Button onClick={openCreate} disabled={!orgId}>
              Create invoice
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {!orgId ? (
            <p className="text-sm text-slate-500">Select an organization first.</p>
          ) : isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : filteredInvoices.length === 0 ? (
            <p className="text-sm text-slate-500">No invoices match the filter.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">#</th>
                    <th className="text-left py-2">Lead</th>
                    <th className="text-left py-2">Status</th>
                    <th className="text-left py-2">Date</th>
                    <th className="text-left py-2">Due date</th>
                    <th className="text-right py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredInvoices.map((inv) => (
                    <tr key={inv.id} className="border-b">
                      <td className="py-2 font-medium">#{inv.index ?? inv.id.slice(0, 8)}</td>
                      <td className="py-2">{leadName(inv.lead_id)}</td>
                      <td className="py-2">{inv.status}</td>
                      <td className="py-2">
                        {inv.date ? new Date(inv.date).toLocaleDateString() : '—'}
                      </td>
                      <td className="py-2">
                        {inv.due_date ? new Date(inv.due_date).toLocaleDateString() : '—'}
                      </td>
                      <td className="py-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(inv)}>
                          Edit
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteInvoice.mutate(inv.id)}
                          disabled={deleteInvoice.isPending}
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

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="Create invoice">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Lead</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={leadId}
              onChange={(e) => setLeadId(e.target.value)}
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
            <label className="block text-sm font-medium mb-1">Status</label>
            <select className="w-full border rounded px-3 py-2" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="paid">Paid</option>
              <option value="overdue">Overdue</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Date</label>
            <Input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Due date</label>
            <Input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Reference</label>
            <Input value={reference} onChange={(e) => setReference(e.target.value)} placeholder="Optional" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Notes</label>
            <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={createInvoice.isPending}>
              Create
            </Button>
          </div>
        </div>
      </Modal>

      <Modal open={editId != null} onClose={() => setEditId(null)} title="Edit invoice">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Status</label>
            <select className="w-full border rounded px-3 py-2" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="paid">Paid</option>
              <option value="overdue">Overdue</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Date</label>
            <Input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Due date</label>
            <Input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Reference</label>
            <Input value={reference} onChange={(e) => setReference(e.target.value)} placeholder="Optional" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Notes</label>
            <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setEditId(null)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={updateInvoice.isPending}>
              Save
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
