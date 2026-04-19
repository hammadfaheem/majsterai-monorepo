import { useState } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminOrgsQueryOptions } from '@/queries/admin-orgs'
import { api } from '@/utils/api'
import type { AdminOrganization, AdminOrganizationUpdate } from '@/types/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { Modal } from '@/components/Modal'

const COUNTRIES = [
  { code: 'AU', name: 'Australia' },
  { code: 'US', name: 'United States' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'PL', name: 'Poland' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'CA', name: 'Canada' },
  { code: 'NZ', name: 'New Zealand' },
  { code: 'JP', name: 'Japan' },
]

export const Route = createFileRoute('/_auth/organizations')({
  loader: ({ context }) => context.queryClient.ensureQueryData(adminOrgsQueryOptions()),
  component: OrganizationsPage,
})

function formatDate(ts: number) {
  return new Date(ts * 1000).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function OrganizationsPage() {
  const queryClient = useQueryClient()
  const { data: orgs = [], isError, error } = useQuery(adminOrgsQueryOptions())

  const [editOrg, setEditOrg] = useState<AdminOrganization | null>(null)
  const [form, setForm] = useState<AdminOrganizationUpdate>({})

  function openEdit(org: AdminOrganization) {
    setEditOrg(org)
    setForm({
      name: org.name,
      time_zone: org.time_zone,
      country: org.country ?? '',
      currency: org.currency,
      tag: org.tag ?? '',
      seats: org.seats ?? undefined,
    })
  }

  const updateOrg = useMutation({
    mutationFn: (orgId: string) =>
      api
        .put<AdminOrganization>(`/api/admin/organizations/${orgId}`, form)
        .then((r) => r.data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['admin', 'organizations'] })
      setEditOrg(null)
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Organizations</h1>
          <p className="mt-1 text-sm text-slate-500">All organizations on the platform.</p>
        </div>
        <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
          {orgs.length} total
        </span>
      </div>

      {isError && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error instanceof Error ? error.message : 'Failed to load organizations'}
        </p>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">All organizations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Name</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Slug</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Plan</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Tag</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Seats</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Country</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-600">Created</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {orgs.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-400">
                      No organizations found.
                    </td>
                  </tr>
                ) : (
                  orgs.map((org) => (
                    <tr key={org.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-2">
                        <Link
                          to="/organizations/$orgId"
                          params={{ orgId: org.id }}
                          className="font-medium text-slate-900 hover:text-accent hover:underline"
                        >
                          {org.name}
                        </Link>
                      </td>
                      <td className="py-3 px-2 text-slate-500 font-mono text-xs">{org.slug}</td>
                      <td className="py-3 px-2">
                        {org.stripe_plan ? (
                          <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                            {org.stripe_plan}
                          </span>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                      <td className="py-3 px-2 text-slate-500">{org.tag ?? '—'}</td>
                      <td className="py-3 px-2 text-slate-500">{org.seats ?? '—'}</td>
                      <td className="py-3 px-2 text-slate-500">{org.country ?? '—'}</td>
                      <td className="py-3 px-2 text-slate-500">{formatDate(org.created_at)}</td>
                      <td className="py-3 px-2 text-right">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(org)}>
                          Edit
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
        open={!!editOrg}
        onClose={() => setEditOrg(null)}
        title={`Edit: ${editOrg?.name ?? ''}`}
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Name</label>
            <Input
              value={form.name ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Time zone</label>
            <Input
              value={form.time_zone ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, time_zone: e.target.value }))}
              placeholder="UTC"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Country</label>
            <select
              value={form.country ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, country: e.target.value }))}
              className="w-full h-10 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950"
            >
              <option value="">Select country</option>
              {COUNTRIES.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Currency</label>
            <Input
              value={form.currency ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, currency: e.target.value }))}
              placeholder="USD"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Tag</label>
            <Input
              value={form.tag ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, tag: e.target.value }))}
              placeholder="Optional"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Seats</label>
            <Input
              type="number"
              value={form.seats ?? ''}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  seats: e.target.value ? parseInt(e.target.value, 10) : undefined,
                }))
              }
              placeholder="Optional"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setEditOrg(null)}>
              Cancel
            </Button>
            <Button
              onClick={() => editOrg && updateOrg.mutate(editOrg.id)}
              disabled={updateOrg.isPending}
            >
              {updateOrg.isPending ? 'Saving…' : 'Save'}
            </Button>
          </div>
          {updateOrg.isError && (
            <p className="text-sm text-red-600">
              {updateOrg.error instanceof Error ? updateOrg.error.message : 'Save failed'}
            </p>
          )}
        </div>
      </Modal>
    </div>
  )
}
