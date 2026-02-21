/** Transfers – list and CRUD for call transfer config. */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

interface Transfer {
  id: string
  org_id: string
  label: string
  method: string
  destination_type: string
  destination: string
  summary_format: string | null
}

export function TransfersPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''
  const [modalOpen, setModalOpen] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [label, setLabel] = useState('')
  const [method, setMethod] = useState('COLD')
  const [destinationType, setDestinationType] = useState('PHONE')
  const [destination, setDestination] = useState('')
  const [summaryFormat, setSummaryFormat] = useState('')

  const { data: transfers = [] } = useQuery({
    queryKey: ['transfers', orgId],
    queryFn: async () => {
      const { data } = await apiClient.get<Transfer[]>(`/api/transfers/org/${orgId}`)
      return data
    },
    enabled: !!orgId,
  })

  const createTransfer = useMutation({
    mutationFn: () =>
      apiClient.post<Transfer>('/api/transfers/', {
        org_id: orgId,
        label,
        method,
        destination_type: destinationType,
        destination,
        summary_format: summaryFormat || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transfers', orgId] })
      setModalOpen(false)
      resetForm()
    },
  })

  const updateTransfer = useMutation({
    mutationFn: (id: string) =>
      apiClient.put<Transfer>(`/api/transfers/${id}`, {
        label,
        method,
        destination_type: destinationType,
        destination,
        summary_format: summaryFormat || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transfers', orgId] })
      setModalOpen(false)
      setEditId(null)
      resetForm()
    },
  })

  const deleteTransfer = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/transfers/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transfers', orgId] }),
  })

  function resetForm() {
    setLabel('')
    setMethod('COLD')
    setDestinationType('PHONE')
    setDestination('')
    setSummaryFormat('')
  }

  const openAdd = () => {
    setEditId(null)
    resetForm()
    setModalOpen(true)
  }

  const openEdit = (t: Transfer) => {
    setEditId(t.id)
    setLabel(t.label)
    setMethod(t.method)
    setDestinationType(t.destination_type)
    setDestination(t.destination)
    setSummaryFormat(t.summary_format ?? '')
    setModalOpen(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editId) {
      updateTransfer.mutate(editId)
    } else {
      createTransfer.mutate()
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Transfers</h1>
          <p className="mt-2 text-sm text-slate-600">
            Call transfer destinations
          </p>
        </div>
        <Button variant="accent" onClick={openAdd}>
          Add transfer
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All transfers</CardTitle>
        </CardHeader>
        <CardContent>
          {transfers.length === 0 ? (
            <p className="text-sm text-slate-500">No transfers yet.</p>
          ) : (
            <ul className="space-y-2">
              {transfers.map((t) => (
                <li
                  key={t.id}
                  className="flex items-center justify-between rounded border border-slate-100 py-2 px-3 text-sm"
                >
                  <div>
                    <span className="font-medium">{t.label}</span>
                    <span className="ml-2 text-slate-500">
                      {t.method} → {t.destination_type}: {t.destination}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm" onClick={() => openEdit(t)}>
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600"
                      onClick={() => {
                        if (window.confirm('Delete this transfer?')) {
                          deleteTransfer.mutate(t.id)
                        }
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? 'Edit transfer' : 'Add transfer'}>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-700">Label</label>
            <Input value={label} onChange={(e) => setLabel(e.target.value)} className="mt-1" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Method</label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="COLD">COLD</option>
              <option value="WARM">WARM</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Destination type</label>
            <select
              value={destinationType}
              onChange={(e) => setDestinationType(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="DEPARTMENT">DEPARTMENT</option>
              <option value="MEMBER">MEMBER</option>
              <option value="PHONE">PHONE</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Destination</label>
            <Input value={destination} onChange={(e) => setDestination(e.target.value)} className="mt-1" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Summary format</label>
            <Input value={summaryFormat} onChange={(e) => setSummaryFormat(e.target.value)} className="mt-1" />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="accent" disabled={createTransfer.isPending || updateTransfer.isPending}>
              {editId ? 'Save' : 'Add'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
