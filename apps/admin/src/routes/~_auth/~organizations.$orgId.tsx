import { useState, useEffect } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminOrgQueryOptions } from '@/queries/admin-orgs'
import { api } from '@/utils/api'
import type { AdminOrganization, AdminOrganizationUpdate } from '@/types/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { ChevronRight } from 'lucide-react'

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

export const Route = createFileRoute('/_auth/organizations/$orgId')({
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(adminOrgQueryOptions(params.orgId)),
  component: OrgDetailPage,
})

function formatDate(ts: number) {
  return new Date(ts * 1000).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function OrgDetailPage() {
  const { orgId } = Route.useParams()
  const queryClient = useQueryClient()
  const { data: org, isError, error } = useQuery(adminOrgQueryOptions(orgId))

  const [form, setForm] = useState<AdminOrganizationUpdate>({})
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (org) {
      setForm({
        name: org.name,
        time_zone: org.time_zone,
        country: org.country ?? '',
        currency: org.currency,
        tag: org.tag ?? '',
        seats: org.seats ?? undefined,
      })
    }
  }, [org])

  const updateOrg = useMutation({
    mutationFn: () =>
      api
        .put<AdminOrganization>(`/api/admin/organizations/${orgId}`, form)
        .then((r) => r.data),
    onSuccess: (updated) => {
      queryClient.setQueryData(['admin', 'organizations', orgId], updated)
      void queryClient.invalidateQueries({ queryKey: ['admin', 'organizations'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    },
  })

  if (isError) {
    return (
      <p className="text-sm text-red-600">
        {error instanceof Error ? error.message : 'Failed to load organization'}
      </p>
    )
  }

  if (!org) return null

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm text-slate-500">
        <Link to="/organizations" className="hover:text-slate-900">
          Organizations
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-slate-900 font-medium">{org.name}</span>
      </nav>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Info card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Details</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3 text-sm">
              {(
                [
                  ['ID', org.id],
                  ['Slug', org.slug],
                  ['Time zone', org.time_zone],
                  ['Country', org.country ?? '—'],
                  ['Currency', org.currency],
                  ['Plan', org.stripe_plan ?? '—'],
                  ['Stripe customer', org.stripe_customer_id ?? '—'],
                  ['Seats', org.seats ?? '—'],
                  ['Tag', org.tag ?? '—'],
                  ['Created', formatDate(org.created_at)],
                ] as [string, string | number][]
              ).map(([label, value]) => (
                <div key={label} className="flex gap-4">
                  <dt className="w-36 flex-shrink-0 font-medium text-slate-600">{label}</dt>
                  <dd className="text-slate-900 break-all font-mono text-xs">{String(value)}</dd>
                </div>
              ))}
              {org.addons && (
                <div className="flex gap-4">
                  <dt className="w-36 flex-shrink-0 font-medium text-slate-600">Add-ons</dt>
                  <dd className="text-slate-900 font-mono text-xs break-all">
                    {JSON.stringify(org.addons)}
                  </dd>
                </div>
              )}
            </dl>
          </CardContent>
        </Card>

        {/* Edit form card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Edit organization</CardTitle>
          </CardHeader>
          <CardContent>
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

              <div className="flex items-center gap-3 pt-2">
                <Button onClick={() => updateOrg.mutate()} disabled={updateOrg.isPending}>
                  {updateOrg.isPending ? 'Saving…' : 'Save changes'}
                </Button>
                {saved && <span className="text-sm text-green-600">Saved!</span>}
                {updateOrg.isError && (
                  <span className="text-sm text-red-600">
                    {updateOrg.error instanceof Error ? updateOrg.error.message : 'Save failed'}
                  </span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
