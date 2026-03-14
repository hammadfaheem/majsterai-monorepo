/** Scenarios – list and CRUD for conversation scenarios. */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

interface Scenario {
  id: string
  org_id: string
  name: string
  prompt: string | null
  response: string | null
  trigger_type: string | null
  trigger_value: string | null
  is_active: boolean
  trade_service_id: number | null
}

export function ScenariosPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''
  const [modalOpen, setModalOpen] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [triggerType, setTriggerType] = useState('KEYWORD')
  const [triggerValue, setTriggerValue] = useState('')
  const [isActive, setIsActive] = useState(true)

  const { data: scenarios = [] } = useQuery({
    queryKey: ['scenarios', orgId],
    queryFn: async () => {
      const { data } = await apiClient.get<Scenario[]>(`/api/scenarios/org/${orgId}`)
      return data
    },
    enabled: !!orgId,
  })

  const createScenario = useMutation({
    mutationFn: () =>
      apiClient.post<Scenario>('/api/scenarios/', {
        org_id: orgId,
        name,
        prompt: prompt || null,
        response: response || null,
        trigger_type: triggerType,
        trigger_value: triggerValue || null,
        is_active: isActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios', orgId] })
      setModalOpen(false)
      setName('')
      setPrompt('')
      setResponse('')
      setTriggerType('KEYWORD')
      setTriggerValue('')
      setIsActive(true)
      setEditId(null)
    },
  })

  const updateScenario = useMutation({
    mutationFn: (id: string) =>
      apiClient.put<Scenario>(`/api/scenarios/${id}`, {
        name,
        prompt: prompt || null,
        response: response || null,
        trigger_type: triggerType,
        trigger_value: triggerValue || null,
        is_active: isActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios', orgId] })
      setModalOpen(false)
      setEditId(null)
    },
  })

  const deleteScenario = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/scenarios/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['scenarios', orgId] }),
  })

  const openAdd = () => {
    setEditId(null)
    setName('')
    setPrompt('')
    setResponse('')
    setTriggerType('KEYWORD')
    setTriggerValue('')
    setIsActive(true)
    setModalOpen(true)
  }

  const openEdit = (s: Scenario) => {
    setEditId(s.id)
    setName(s.name)
    setPrompt(s.prompt ?? '')
    setResponse(s.response ?? '')
    setTriggerType(s.trigger_type ?? 'KEYWORD')
    setTriggerValue(s.trigger_value ?? '')
    setIsActive(s.is_active)
    setModalOpen(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editId) updateScenario.mutate(editId)
    else createScenario.mutate()
  }

  if (!currentOrganization) {
    return (
      <div className="text-slate-600 dark:text-slate-400">
        Select an organization to configure scenarios.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Scenarios</h1>
          <p className="mt-2 text-sm text-slate-600">Conversation flows and responses</p>
        </div>
        <Button variant="accent" onClick={openAdd}>Add scenario</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>All scenarios</CardTitle></CardHeader>
        <CardContent>
          {scenarios.length === 0 ? (
            <p className="text-sm text-slate-500">No scenarios yet.</p>
          ) : (
            <ul className="space-y-2">
              {scenarios.map((s) => (
                <li key={s.id} className="flex items-center justify-between rounded border border-slate-100 py-2 px-3 text-sm">
                  <div>
                    <span className="font-medium">{s.name}</span>
                    {!s.is_active && <span className="ml-2 text-xs text-slate-400">(inactive)</span>}
                    {s.trigger_type && <span className="ml-2 text-slate-500">{s.trigger_type}: {s.trigger_value ?? '—'}</span>}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm" onClick={() => openEdit(s)}>Edit</Button>
                    <Button variant="ghost" size="sm" className="text-red-600" onClick={() => window.confirm('Delete?') && deleteScenario.mutate(s.id)}>Delete</Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? 'Edit scenario' : 'Add scenario'}>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-700">Name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} className="mt-1" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Prompt</label>
            <Input value={prompt} onChange={(e) => setPrompt(e.target.value)} className="mt-1" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Response</label>
            <Input value={response} onChange={(e) => setResponse(e.target.value)} className="mt-1" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Trigger type</label>
            <select value={triggerType} onChange={(e) => setTriggerType(e.target.value)} className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm">
              <option value="KEYWORD">KEYWORD</option>
              <option value="INTENT">INTENT</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Trigger value</label>
            <Input value={triggerValue} onChange={(e) => setTriggerValue(e.target.value)} className="mt-1" />
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="scenario-active" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} className="rounded border-slate-300" />
            <label htmlFor="scenario-active" className="text-sm text-slate-700">Active</label>
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="accent" disabled={createScenario.isPending || updateScenario.isPending}>{editId ? 'Save' : 'Add'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
