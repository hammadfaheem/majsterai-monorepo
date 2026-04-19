import { useState } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminUsersQueryOptions } from '@/queries/admin-users'
import { api } from '@/utils/api'
import type { AdminUser } from '@/types/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { Button } from '@/components/Button'
import { Modal } from '@/components/Modal'
import { StatusBadge } from '@/components/StatusBadge'

const PLATFORM_ROLES = ['SUPERADMIN', 'STAFF', 'CUSTOMER'] as const

export const Route = createFileRoute('/_auth/users')({
  loader: ({ context }) => context.queryClient.ensureQueryData(adminUsersQueryOptions()),
  component: UsersPage,
})

function formatDate(ts: number) {
  return new Date(ts * 1000).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function UsersPage() {
  const queryClient = useQueryClient()
  const { data: users = [], isError, error } = useQuery(adminUsersQueryOptions())

  const [editUser, setEditUser] = useState<AdminUser | null>(null)
  const [role, setRole] = useState<string>('CUSTOMER')

  function openEdit(u: AdminUser) {
    setEditUser(u)
    setRole(u.role ?? 'CUSTOMER')
  }

  const updateUser = useMutation({
    mutationFn: (userId: string) =>
      api
        .patch<AdminUser>(`/api/admin/users/${userId}`, { role: role || null })
        .then((r) => r.data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['admin', 'users'] })
      setEditUser(null)
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Users</h1>
          <p className="mt-1 text-sm text-slate-500">All platform users across all organizations.</p>
        </div>
        <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
          {users.length} total
        </span>
      </div>

      {isError && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error instanceof Error ? error.message : 'Failed to load users'}
        </p>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">All users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Name</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Email</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Role</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Created</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-400">
                      No users found.
                    </td>
                  </tr>
                ) : (
                  users.map((u) => (
                    <tr key={u.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-2 font-medium text-slate-900">{u.name}</td>
                      <td className="py-3 px-2 text-slate-600">{u.email}</td>
                      <td className="py-3 px-2">
                        <StatusBadge status={u.role ?? 'CUSTOMER'} />
                      </td>
                      <td className="py-3 px-2 text-slate-500">{formatDate(u.created_at)}</td>
                      <td className="py-3 px-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(u)}>
                          Edit role
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Modal
        open={!!editUser}
        onClose={() => setEditUser(null)}
        title={`Edit role: ${editUser?.name ?? ''}`}
      >
        <div className="space-y-4">
          <div>
            <p className="text-sm text-slate-500 mb-4">{editUser?.email}</p>
            <label className="block text-sm font-medium text-slate-700 mb-1">Platform role</label>
            <select
              className="w-full h-10 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950"
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
            <Button variant="outline" onClick={() => setEditUser(null)}>
              Cancel
            </Button>
            <Button
              onClick={() => editUser && updateUser.mutate(editUser.id)}
              disabled={updateUser.isPending}
            >
              {updateUser.isPending ? 'Saving…' : 'Save'}
            </Button>
          </div>
          {updateUser.isError && (
            <p className="text-sm text-red-600">
              {updateUser.error instanceof Error ? updateUser.error.message : 'Save failed'}
            </p>
          )}
        </div>
      </Modal>
    </div>
  )
}
