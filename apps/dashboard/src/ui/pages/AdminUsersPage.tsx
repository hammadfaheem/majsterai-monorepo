/** Platform admin – list and edit all users (platform role). */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminService } from '@/application/admin/adminService'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Modal } from '@/ui/components/Modal'

const PLATFORM_ROLES = ['SUPERADMIN', 'STAFF', 'CUSTOMER'] as const

export function AdminUsersPage() {
  const queryClient = useQueryClient()
  const [editId, setEditId] = useState<string | null>(null)
  const [role, setRole] = useState<string>('CUSTOMER')

  const { data: users = [], isLoading, isError, error } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminService.listUsers(),
  })

  const updateUser = useMutation({
    mutationFn: (userId: string) => adminService.updateUser(userId, { role: role || null }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      setEditId(null)
    },
  })

  const openEdit = (u: { id: string; email: string; name: string; role: string | null }) => {
    setEditId(u.id)
    setRole(u.role ?? 'CUSTOMER')
  }

  const handleSave = () => {
    if (editId) updateUser.mutate(editId)
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Platform Admin – Users</h1>
        <p className="mt-2 text-sm text-slate-600">View and edit platform roles (superadmin only).</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All users</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : isError ? (
            <p className="text-sm text-red-600">{error instanceof Error ? error.message : 'Failed to load'}</p>
          ) : users.length === 0 ? (
            <p className="text-sm text-slate-500">No users.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Email</th>
                    <th className="text-left py-2">Name</th>
                    <th className="text-left py-2">Role</th>
                    <th className="text-right py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-b">
                      <td className="py-2">{u.email}</td>
                      <td className="py-2">{u.name}</td>
                      <td className="py-2">{u.role ?? '—'}</td>
                      <td className="py-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(u)}>
                          Edit
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

      <Modal open={!!editId} onClose={() => setEditId(null)} title="Edit user role">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Platform role</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              {PLATFORM_ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setEditId(null)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={updateUser.isPending}>
              Save
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
