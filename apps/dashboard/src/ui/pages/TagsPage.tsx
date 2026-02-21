/** Tags (tag bases) – list and CRUD for org-level tag definitions. */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

interface TagBase {
  id: string
  org_id: string
  value: string
  color: string | null
  type: string
  description: string | null
  is_enabled: boolean
  created_at: number
  updated_at: number
}

export function TagsPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''
  const [modalOpen, setModalOpen] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [value, setValue] = useState('')
  const [color, setColor] = useState('')
  const [type, setType] = useState('LEAD')
  const [description, setDescription] = useState('')
  const [isEnabled, setIsEnabled] = useState(true)

  const { data: tags = [] } = useQuery({
    queryKey: ['tag-bases', orgId],
    queryFn: async () => {
      const { data } = await apiClient.get<TagBase[]>(`/api/tag-bases/org/${orgId}`)
      return data
    },
    enabled: !!orgId,
  })

  const createTag = useMutation({
    mutationFn: () =>
      apiClient.post<TagBase>('/api/tag-bases/', {
        org_id: orgId,
        value,
        color: color || null,
        type,
        description: description || null,
        is_enabled: isEnabled,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tag-bases', orgId] })
      setModalOpen(false)
      setValue('')
      setColor('')
      setType('LEAD')
      setDescription('')
      setIsEnabled(true)
      setEditId(null)
    },
  })

  const updateTag = useMutation({
    mutationFn: (id: string) =>
      apiClient.put<TagBase>(`/api/tag-bases/${id}`, {
        value,
        color: color || null,
        type,
        description: description || null,
        is_enabled: isEnabled,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tag-bases', orgId] })
      setModalOpen(false)
      setEditId(null)
    },
  })

  const deleteTag = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/tag-bases/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tag-bases', orgId] }),
  })

  const openAdd = () => {
    setEditId(null)
    setValue('')
    setColor('')
    setType('LEAD')
    setDescription('')
    setIsEnabled(true)
    setModalOpen(true)
  }

  const openEdit = (t: TagBase) => {
    setEditId(t.id)
    setValue(t.value)
    setColor(t.color ?? '')
    setType(t.type)
    setDescription(t.description ?? '')
    setIsEnabled(t.is_enabled)
    setModalOpen(true)
  }

  const handleSubmit = () => {
    if (!value.trim()) return
    if (editId) updateTag.mutate(editId)
    else createTag.mutate()
  }

  return (
    <div className="p-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Tags</CardTitle>
          <Button onClick={openAdd} disabled={!orgId}>
            Add tag
          </Button>
        </CardHeader>
        <CardContent>
          {!orgId ? (
            <p className="text-muted-foreground">Select an organization first.</p>
          ) : tags.length === 0 ? (
            <p className="text-muted-foreground">No tags yet. Add one to organize leads and inquiries.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Value</th>
                    <th className="text-left py-2">Color</th>
                    <th className="text-left py-2">Type</th>
                    <th className="text-left py-2">Description</th>
                    <th className="text-left py-2">Enabled</th>
                    <th className="text-right py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tags.map((t) => (
                    <tr key={t.id} className="border-b">
                      <td className="py-2">{t.value}</td>
                      <td className="py-2">
                        {t.color ? (
                          <span
                            className="inline-block w-5 h-5 rounded border"
                            style={{ backgroundColor: t.color }}
                            title={t.color}
                          />
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="py-2">{t.type}</td>
                      <td className="py-2 max-w-[200px] truncate">{t.description ?? '—'}</td>
                      <td className="py-2">{t.is_enabled ? 'Yes' : 'No'}</td>
                      <td className="py-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(t)}>
                          Edit
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteTag.mutate(t.id)}
                          disabled={deleteTag.isPending}
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

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? 'Edit tag' : 'Add tag'}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Value</label>
            <Input value={value} onChange={(e) => setValue(e.target.value)} placeholder="e.g. Hot lead" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Color (hex, optional)</label>
            <Input value={color} onChange={(e) => setColor(e.target.value)} placeholder="#3b82f6" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Type</label>
            <select className="w-full border rounded px-3 py-2" value={type} onChange={(e) => setType(e.target.value)}>
              <option value="LEAD">LEAD</option>
              <option value="INQUIRY">INQUIRY</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional" />
          </div>
          <div>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={isEnabled} onChange={(e) => setIsEnabled(e.target.checked)} />
              <span className="text-sm">Enabled</span>
            </label>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={!value.trim() || createTag.isPending || updateTag.isPending}>
              {editId ? 'Save' : 'Create'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
