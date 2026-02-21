/** Dashboard page with metrics and overview. */

import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import { useUIStore } from '@/store/ui.store'
import { useOrganization } from '@/application/organization/organizationContext'
import { callHistoryService } from '@/application/call_history/callHistoryService'
import { leadService } from '@/application/lead/leadService'
import { appointmentService } from '@/application/appointment/appointmentService'
import { taskService } from '@/application/task/taskService'
import { MetricCard } from '@/ui/components/MetricCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'

const LEAD_STATUS_COLORS: Record<string, string> = {
  new: '#64748b',
  contacted: '#3b82f6',
  qualified: '#8b5cf6',
  converted: '#22c55e',
  lost: '#ef4444',
}

export function DashboardPage() {
  const theme = useUIStore((s) => s.theme)
  const isDark = theme === 'dark'
  const { currentOrganization } = useOrganization()

  const chartTextColor = isDark ? '#94a3b8' : '#475569'
  const chartTooltipBg = isDark ? '#1e293b' : '#ffffff'
  const chartTooltipBorder = isDark ? '#334155' : '#e2e8f0'
  const chartBarFill = isDark ? '#818cf8' : '#6366f1'

  const { data: analytics } = useQuery({
    queryKey: ['call-analytics', currentOrganization?.id],
    queryFn: () => callHistoryService.getAnalytics(currentOrganization?.id || ''),
    enabled: !!currentOrganization?.id,
  })

  const { data: leads = [] } = useQuery({
    queryKey: ['leads', currentOrganization?.id],
    queryFn: () => leadService.listLeads(currentOrganization?.id || '', { limit: 500 }),
    enabled: !!currentOrganization?.id,
  })

  const { data: calls = [] } = useQuery({
    queryKey: ['call-history', currentOrganization?.id],
    queryFn: () => callHistoryService.listCalls(currentOrganization?.id || '', { limit: 100 }),
    enabled: !!currentOrganization?.id,
  })

  const { data: appointments = [] } = useQuery({
    queryKey: ['appointments', currentOrganization?.id],
    queryFn: () => appointmentService.list(currentOrganization?.id ?? '', { limit: 500 }),
    enabled: !!currentOrganization?.id,
  })

  const { data: tasks = [] } = useQuery({
    queryKey: ['tasks', currentOrganization?.id],
    queryFn: () => taskService.listTasks(currentOrganization?.id ?? ''),
    enabled: !!currentOrganization?.id,
  })

  const now = Date.now()
  const next7Days = now + 7 * 24 * 60 * 60 * 1000
  const upcomingAppointments = useMemo(
    () =>
      appointments
        .filter((a) => a.start >= now && a.start <= next7Days && a.status !== 'cancelled')
        .sort((a, b) => a.start - b.start)
        .slice(0, 10),
    [appointments]
  )
  const incompleteTasks = useMemo(
    () => tasks.filter((t) => !t.is_completed).slice(0, 10),
    [tasks]
  )

  const leadStatusData = useMemo(() => {
    const byStatus: Record<string, number> = {}
    for (const lead of leads) {
      byStatus[lead.status] = (byStatus[lead.status] ?? 0) + 1
    }
    return Object.entries(byStatus).map(([name, value]) => ({ name, value }))
  }, [leads])

  const callsByDateData = useMemo(() => {
    const byDate: Record<string, { count: number; created_at: number }> = {}
    for (const call of calls) {
      const date = new Date(call.created_at * 1000).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      })
      if (!byDate[date]) byDate[date] = { count: 0, created_at: call.created_at }
      byDate[date].count += 1
    }
    return Object.entries(byDate)
      .sort((a, b) => a[1].created_at - b[1].created_at)
      .map(([date, { count }]) => ({ date, count }))
  }, [calls])

  const recentLeads = useMemo(() => leads.slice(0, 5), [leads])
  const recentCalls = useMemo(() => calls.slice(0, 5), [calls])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          Overview of your voice AI agent performance
        </p>
      </div>

      {/* Metrics - 5 cards in one row on large screens */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
        <MetricCard
          title="Total Calls"
          value={analytics?.total_calls ?? 0}
          description="All time calls"
        />
        <MetricCard
          title="Completed Calls"
          value={analytics?.completed_calls ?? 0}
          description="Successfully completed"
        />
        <MetricCard
          title="Avg Duration"
          value={`${Math.round((analytics?.average_duration_seconds ?? 0) / 60)}m`}
          description="Average call length"
        />
        <MetricCard
          title="Total Leads"
          value={leads.length}
          description="Active leads"
        />
        <MetricCard
          title="Appointments"
          value={appointments.length}
          description="Scheduled"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Calls over time</CardTitle>
          </CardHeader>
          <CardContent>
            {callsByDateData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={callsByDateData}>
                    <XAxis dataKey="date" tick={{ fontSize: 12, fill: chartTextColor }} stroke={chartTextColor} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: chartTextColor }} stroke={chartTextColor} />
                    <Tooltip
                      contentStyle={{
                        borderRadius: '8px',
                        border: `1px solid ${chartTooltipBorder}`,
                        backgroundColor: chartTooltipBg,
                        color: isDark ? '#f1f5f9' : '#0f172a',
                      }}
                    />
                    <Bar dataKey="count" fill={chartBarFill} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">No call data yet</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Lead status</CardTitle>
          </CardHeader>
          <CardContent>
            {leadStatusData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={leadStatusData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {leadStatusData.map((entry) => (
                        <Cell
                          key={entry.name}
                          fill={LEAD_STATUS_COLORS[entry.name] ?? '#94a3b8'}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        borderRadius: '8px',
                        border: `1px solid ${chartTooltipBorder}`,
                        backgroundColor: chartTooltipBg,
                        color: isDark ? '#f1f5f9' : '#0f172a',
                      }}
                    />
                    <Legend wrapperStyle={{ color: chartTextColor }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">No leads yet</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Upcoming & Tasks */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Upcoming appointments</CardTitle>
          </CardHeader>
          <CardContent>
            {upcomingAppointments.length > 0 ? (
              <ul className="space-y-2">
                {upcomingAppointments.map((a) => (
                  <li key={a.id} className="text-sm text-slate-900 dark:text-slate-100">
                    <span className="font-medium">{a.title || 'Appointment'}</span>
                    <span className="text-slate-500 dark:text-slate-400">
                      {' '}
                      – {new Date(a.start).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">No appointments in the next 7 days</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tasks to do</CardTitle>
          </CardHeader>
          <CardContent>
            {incompleteTasks.length > 0 ? (
              <ul className="space-y-2">
                {incompleteTasks.map((t) => (
                  <li key={t.id} className="text-sm text-slate-900 dark:text-slate-100">
                    <span className="font-medium">{t.title}</span>
                    {t.lead_id && (
                      <span className="text-slate-500 dark:text-slate-400"> (lead)</span>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">No pending tasks</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Calls</CardTitle>
          </CardHeader>
          <CardContent>
            {recentCalls.length > 0 ? (
              <ul className="space-y-2">
                {recentCalls.map((call) => (
                  <li key={call.id} className="text-sm text-slate-900 dark:text-slate-100">
                    <span className="font-medium">{call.room_name}</span>
                    <span className="text-slate-500 dark:text-slate-400">
                      {' '}
                      – {call.status} ·{' '}
                      {call.duration != null
                        ? `${Math.round(call.duration / 60)}m`
                        : '—'}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">No recent calls</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Leads</CardTitle>
          </CardHeader>
          <CardContent>
            {recentLeads.length > 0 ? (
              <ul className="space-y-2">
                {recentLeads.map((lead) => (
                  <li key={lead.id} className="text-sm text-slate-900 dark:text-slate-100">
                    <span className="font-medium">{lead.name}</span>
                    {lead.email && (
                      <span className="text-slate-500 dark:text-slate-400"> – {lead.email}</span>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">No recent leads</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
