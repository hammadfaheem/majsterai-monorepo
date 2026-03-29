/**
 * CalendarSettingsPage — /settings/calendar
 *
 * Allows users to:
 *  1. Connect Google calendar via OAuth (requires GOOGLE_CLIENT_ID in API .env)
 *  2. See + manage their linked calendars (toggle conflict-check, set default)
 *  3. Remove a linked calendar
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { useAppSelector } from '@/store/hooks'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { CalendarDays, Star, Trash2, RefreshCw, Link } from 'lucide-react'

interface SelectedCalendar {
  id: number
  calendar_id: string | null
  calendar_name: string | null
  integration: string | null
  is_default: boolean
  is_active_for_conflict_check: boolean
  member_id: string
  last_synced_at: number | null
  next_async_token: string | null
}

interface GoogleCalendarItem {
  id: string
  name: string
  primary: boolean
  access_role: string
}

export function CalendarSettingsPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const memberId = useAppSelector((s) => s.auth.user?.id ?? '')

  const [credentialId, setCredentialId] = useState<string | null>(null)
  const [connectError, setConnectError] = useState('')

  // --- Linked calendars for this member -----------------------------------
  const { data: linkedCalendars = [], isLoading } = useQuery<SelectedCalendar[]>({
    queryKey: ['selected-calendars', memberId],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/calendar/selected-calendars', {
        params: { member_id: memberId },
      })
      return data
    },
    enabled: !!memberId,
  })

  // --- Available Google calendars (after OAuth) ---------------------------
  const { data: googleCalendars = [] } = useQuery<GoogleCalendarItem[]>({
    queryKey: ['google-calendars', credentialId],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/calendar/google/calendars', {
        params: { credential_id: credentialId },
      })
      return data
    },
    enabled: !!credentialId,
  })

  // --- Mutations ----------------------------------------------------------
  const removeMutation = useMutation({
    mutationFn: (calId: number) =>
      apiClient.delete(`/api/calendar/selected-calendars/${calId}`),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ['selected-calendars', memberId] }),
  })

  const setDefaultMutation = useMutation({
    mutationFn: (calId: number) =>
      apiClient.put(`/api/calendar/selected-calendars/${calId}/set-default`, null, {
        params: { member_id: memberId },
      }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ['selected-calendars', memberId] }),
  })

  const linkGoogleMutation = useMutation({
    mutationFn: async (cal: GoogleCalendarItem) => {
      const { data } = await apiClient.post('/api/calendar/selected-calendars', {
        member_id: memberId,
        org_id: currentOrganization?.id,
        credential_id: credentialId,
        calendar_id: cal.id,
        calendar_name: cal.name,
        integration: 'google',
        is_default: cal.primary,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['selected-calendars', memberId] })
      setCredentialId(null)
    },
  })

  const syncMutation = useMutation({
    mutationFn: (calId: number) =>
      apiClient.post('/api/calendar/google/sync', null, {
        params: { selected_calendar_id: calId },
      }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ['selected-calendars', memberId] }),
  })

  // --- Connect Google (open OAuth URL in current tab) --------------------
  const handleConnectGoogle = async () => {
    if (!currentOrganization?.id) return
    setConnectError('')
    try {
      const redirectUri = `${window.location.origin}/settings/calendar?oauth=google`
      const { data } = await apiClient.get('/api/calendar/google/auth-url', {
        params: { org_id: currentOrganization.id, redirect_uri: redirectUri },
      })
      window.location.href = data.url
    } catch {
      setConnectError('Google OAuth is not configured. Set GOOGLE_CLIENT_ID in the API .env file.')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
          Calendar
        </h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          Connect external calendars for conflict checking and automatic event sync.
        </p>
      </div>

      {/* Connect new calendar */}
      <Card>
        <CardHeader>
          <CardTitle>Connect a calendar</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Link your Google or Outlook calendar. New appointments will be pushed there
            automatically and external events will be shown on the calendar to avoid
            double-booking.
          </p>
          {connectError && (
            <p className="text-sm text-red-500">{connectError}</p>
          )}
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleConnectGoogle} className="gap-2">
              <Link className="h-4 w-4" />
              Connect Google Calendar
            </Button>
            <Button variant="outline" disabled className="gap-2 opacity-50">
              <Link className="h-4 w-4" />
              Connect Outlook (coming soon)
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Available Google calendars (shown after OAuth returns credentialId) */}
      {credentialId && googleCalendars.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Select calendars to link</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {googleCalendars.map((cal) => (
              <div
                key={cal.id}
                className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3 dark:border-slate-700"
              >
                <div>
                  <p className="text-sm font-medium">{cal.name}</p>
                  <p className="text-xs text-slate-500">{cal.id}</p>
                </div>
                <Button
                  variant="accent"
                  onClick={() => linkGoogleMutation.mutate(cal)}
                  disabled={linkGoogleMutation.isPending}
                  className="px-3 py-1 text-xs"
                >
                  Link
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Linked calendars */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CalendarDays className="h-4 w-4" />
            Linked calendars
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : linkedCalendars.length === 0 ? (
            <p className="text-sm text-slate-500">
              No calendars linked yet. Connect one above.
            </p>
          ) : (
            <ul className="space-y-3">
              {linkedCalendars.map((cal) => (
                <li
                  key={cal.id}
                  className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3 dark:border-slate-700"
                >
                  <div className="flex items-center gap-3">
                    <CalendarDays className="h-4 w-4 text-slate-400" />
                    <div>
                      <p className="text-sm font-medium">
                        {cal.calendar_name || cal.calendar_id}
                        {cal.is_default && (
                          <span className="ml-2 rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                            Default
                          </span>
                        )}
                      </p>
                      <p className="text-xs text-slate-500 capitalize">
                        {cal.integration ?? 'unknown'} ·{' '}
                        {cal.last_synced_at
                          ? `Last synced ${new Date(cal.last_synced_at).toLocaleString()}`
                          : 'Never synced'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {!cal.is_default && (
                      <button
                        title="Set as default"
                        onClick={() => setDefaultMutation.mutate(cal.id)}
                        className="rounded p-1.5 text-slate-400 hover:text-amber-500"
                      >
                        <Star className="h-4 w-4" />
                      </button>
                    )}
                    {cal.integration === 'google' && (
                      <button
                        title="Sync now"
                        onClick={() => syncMutation.mutate(cal.id)}
                        disabled={syncMutation.isPending}
                        className="rounded p-1.5 text-slate-400 hover:text-blue-500 disabled:opacity-40"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      title="Remove"
                      onClick={() => removeMutation.mutate(cal.id)}
                      disabled={removeMutation.isPending}
                      className="rounded p-1.5 text-slate-400 hover:text-red-500 disabled:opacity-40"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {/* Key design notes */}
      <Card>
        <CardHeader>
          <CardTitle>How sync works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
          <p>
            <strong>Push:</strong> when you create or reschedule an appointment, it is
            automatically written to your default connected calendar.
          </p>
          <p>
            <strong>Pull:</strong> clicking "Sync now" fetches changes made directly in
            Google Calendar back into this app using Google's incremental sync (only the
            delta since the last sync is downloaded).
          </p>
          <p>
            <strong>Deduplication:</strong> each appointment stores the external event ID
            in <code>reference_id</code>. If a pulled Google event already exists in the
            database it is skipped — no duplicates.
          </p>
          <p>
            <strong>Soft delete:</strong> appointments are never hard-deleted. When a
            Google event is cancelled, the matching appointment is soft-deleted via
            <code>deleted_at</code>.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
