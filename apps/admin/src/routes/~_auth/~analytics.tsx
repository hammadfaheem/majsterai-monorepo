import { useState } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { adminOrgsQueryOptions } from '@/queries/admin-orgs'
import { analyticsQueryOptions } from '@/queries/analytics'
import { MetricCard } from '@/components/MetricCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'

export const Route = createFileRoute('/_auth/analytics')({
  loader: ({ context }) => context.queryClient.ensureQueryData(adminOrgsQueryOptions()),
  component: AnalyticsPage,
})

function formatDuration(seconds: number) {
  if (!seconds) return '0s'
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  if (m === 0) return `${s}s`
  return `${m}m ${s}s`
}

function AnalyticsPage() {
  const { data: orgs = [] } = useQuery(adminOrgsQueryOptions())
  const [selectedOrgId, setSelectedOrgId] = useState<string>('')

  const { data: analytics, isLoading, isError, error } = useQuery({
    ...analyticsQueryOptions(selectedOrgId),
    enabled: !!selectedOrgId,
  })

  const selectedOrg = orgs.find((o) => o.id === selectedOrgId)

  const chartData = analytics
    ? [
        {
          name: selectedOrg?.name ?? 'Org',
          'Total Calls': analytics.total_calls,
          'Completed': analytics.completed_calls,
        },
      ]
    : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>
        <p className="mt-1 text-sm text-slate-500">Call analytics per organization.</p>
      </div>

      <div className="flex items-center gap-3">
        <label className="text-sm font-medium text-slate-700 flex-shrink-0">Organization</label>
        <select
          value={selectedOrgId}
          onChange={(e) => setSelectedOrgId(e.target.value)}
          className="h-10 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 min-w-64"
        >
          <option value="">Select an organization…</option>
          {orgs.map((org) => (
            <option key={org.id} value={org.id}>
              {org.name}
            </option>
          ))}
        </select>
      </div>

      {!selectedOrgId && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-slate-400 text-sm">Select an organization to view analytics.</p>
        </div>
      )}

      {selectedOrgId && isLoading && (
        <p className="text-sm text-slate-500">Loading analytics…</p>
      )}

      {selectedOrgId && isError && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error instanceof Error ? error.message : 'Failed to load analytics'}
        </p>
      )}

      {analytics && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <MetricCard
              title="Total Calls"
              value={analytics.total_calls}
              description="All calls recorded"
            />
            <MetricCard
              title="Completed Calls"
              value={analytics.completed_calls}
              description="Successfully completed"
            />
            <MetricCard
              title="Avg Duration"
              value={formatDuration(analytics.average_duration_seconds)}
              description="Per completed call"
            />
            <MetricCard
              title="Total Duration"
              value={formatDuration(analytics.total_duration_seconds)}
              description="All calls combined"
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Call volume — {selectedOrg?.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Total Calls" fill="#f97316" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Completed" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
