/** Call history page for viewing call records. */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { callHistoryService } from '@/application/call_history/callHistoryService'
import { DataTable } from '@/ui/components/DataTable'
import { StatusBadge } from '@/ui/components/StatusBadge'
import { useOrganization } from '@/application/organization/organizationContext'
import { Modal } from '@/ui/components/Modal'

export function CallHistoryPage() {
  const { currentOrganization } = useOrganization()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [detailRoomName, setDetailRoomName] = useState<string | null>(null)

  const { data: calls = [], isLoading, isError, error } = useQuery({
    queryKey: ['call-history', currentOrganization?.id],
    queryFn: () => callHistoryService.listCalls(currentOrganization?.id || '', { limit: 500 }),
    enabled: !!currentOrganization?.id,
  })

  const { data: callDetails, isLoading: detailsLoading } = useQuery({
    queryKey: ['call-details', detailRoomName],
    queryFn: () => callHistoryService.getCallDetails(detailRoomName!),
    enabled: !!detailRoomName,
  })

  const filteredCalls = useMemo(() => {
    let list = calls
    if (statusFilter) list = list.filter((c) => c.status === statusFilter)
    return list
  }, [calls, statusFilter])

  const columns = [
    {
      key: 'room_name',
      header: 'Room Name',
    },
    {
      key: 'direction',
      header: 'Direction',
      render: (value: unknown) => <StatusBadge status={String(value)} />,
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: unknown) => <StatusBadge status={String(value)} />,
    },
    {
      key: 'duration',
      header: 'Duration',
      render: (value: unknown) => {
        if (!value) return '-'
        const seconds = Number(value)
        const minutes = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${minutes}m ${secs}s`
      },
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (value: unknown) => {
        if (!value) return '-'
        return new Date(Number(value)).toLocaleString()
      },
    },
  ]

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Call History</h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          View and manage your call records
        </p>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <select
          className="border border-slate-300 dark:border-slate-600 rounded px-3 py-2 text-sm bg-white dark:bg-slate-800 dark:text-slate-100"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800/30">
        {isLoading ? (
          <div className="py-12 text-center text-sm text-slate-500">
            Loading…
          </div>
        ) : isError ? (
          <div className="py-12 text-center">
            <p className="text-sm text-red-600">
              Failed to load calls. {error instanceof Error ? error.message : 'Please try again.'}
            </p>
          </div>
        ) : filteredCalls.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <p className="text-sm text-slate-500 text-center">
              {calls.length === 0
                ? 'No calls yet. Start a test call from Test Agent to see history here.'
                : 'No calls match the selected filter.'}
            </p>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredCalls as unknown as Record<string, unknown>[]}
            onRowClick={(call) => setDetailRoomName((call as { room_name?: string }).room_name ?? null)}
          />
        )}
      </div>

      <Modal
        open={!!detailRoomName}
        onClose={() => setDetailRoomName(null)}
        title="Call details"
      >
        {detailsLoading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : callDetails ? (
          <div className="space-y-4 text-sm">
            {callDetails.call_history?.summary && (
              <div>
                <h3 className="font-medium text-slate-700">Summary</h3>
                <p className="mt-1 text-slate-600 whitespace-pre-wrap">{callDetails.call_history.summary}</p>
              </div>
            )}
            {callDetails.transcript?.transcript && (
              <div>
                <h3 className="font-medium text-slate-700">Transcript</h3>
                <p className="mt-1 text-slate-600 whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {callDetails.transcript.transcript}
                </p>
              </div>
            )}
            {!callDetails.call_history?.summary && !callDetails.transcript?.transcript && (
              <p className="text-slate-500">No summary or transcript available.</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Could not load details.</p>
        )}
      </Modal>
    </div>
  )
}
