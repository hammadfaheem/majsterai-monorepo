/**
 * CalendarView — FullCalendar-based appointment calendar.
 *
 * URL state (via nuqs): view, date, selectedEventId
 * Supports day / week / month views, drag-and-drop rescheduling (15-min snap),
 * click-to-create, and a loading overlay that doesn't unmount the calendar.
 */

import { useRef, useState, useCallback, useMemo } from 'react'
import FullCalendar from '@fullcalendar/react'
import type {
  DatesSetArg,
  EventClickArg,
  EventDropArg,
  DateSelectArg,
  EventInput,
} from '@fullcalendar/core'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { parseAsString, parseAsIsoDate, useQueryStates } from 'nuqs'
import { ChevronLeft, ChevronRight, Calendar, Loader2 } from 'lucide-react'
import { appointmentService } from '@/application/appointment/appointmentService'
import { Button } from '@/ui/components/Button'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type CalendarViewType = 'dayGridMonth' | 'timeGridWeek' | 'timeGridDay'

const VIEW_LABELS: [CalendarViewType, string][] = [
  ['timeGridDay', 'Day'],
  ['timeGridWeek', 'Week'],
  ['dayGridMonth', 'Month'],
]

const STATUS_COLORS: Record<string, string> = {
  PENDING: '#f59e0b',
  CONFIRMED: '#3b82f6',
  IN_PROGRESS: '#8b5cf6',
  COMPLETE: '#10b981',
  CANCELLED: '#ef4444',
  NO_SHOW: '#6b7280',
}

// Round ms to nearest 15-minute boundary (floor, matching guide)
const snapTo15 = (ms: number) => Math.floor(ms / 900_000) * 900_000

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  orgId: string
  /** Called when the user clicks an empty time slot — open a pre-filled create modal */
  onSelectDate?: (start: Date, end: Date) => void
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CalendarView({ orgId, onSelectDate }: Props) {
  const calRef = useRef<FullCalendar>(null)
  const queryClient = useQueryClient()

  // --- URL state (nuqs) ---------------------------------------------------
  const [{ calView, calDate }, setQueryStates] = useQueryStates(
    {
      calView: parseAsString.withDefault('timeGridWeek'),
      calDate: parseAsIsoDate,
    },
    { history: 'push' },
  )

  const view = calView as CalendarViewType

  // --- Local state ---------------------------------------------------------
  const [rangeStart, setRangeStart] = useState(0)
  const [rangeEnd, setRangeEnd] = useState(0)
  const [titleText, setTitleText] = useState('')
  const [pendingDrop, setPendingDrop] = useState<EventDropArg | null>(null)

  // --- Data fetching -------------------------------------------------------
  const { data: appointments = [], isFetching } = useQuery({
    queryKey: ['appointments-calendar', orgId, rangeStart, rangeEnd],
    queryFn: () => appointmentService.listByRange(orgId, rangeStart, rangeEnd),
    enabled: !!orgId && rangeStart > 0,
  })

  const hasAllDay = useMemo(
    () => appointments.some((a) => a.start === a.end),
    [appointments],
  )

  const events: EventInput[] = useMemo(
    () =>
      appointments.map((apt) => ({
        id: apt.id,
        title: apt.title || 'Untitled',
        start: new Date(apt.start),
        end: new Date(apt.end),
        backgroundColor: STATUS_COLORS[apt.status] ?? '#3b82f6',
        borderColor: STATUS_COLORS[apt.status] ?? '#3b82f6',
        extendedProps: {
          status: apt.status,
          leadId: apt.lead_id,
          referenceId: apt.reference_id,
        },
      })),
    [appointments],
  )

  // --- Drag & drop rescheduling -------------------------------------------
  const updateMutation = useMutation({
    mutationFn: ({ id, start, end }: { id: string; start: number; end: number }) =>
      appointmentService.update(id, { start, end, is_rescheduled: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments-calendar', orgId] })
      queryClient.invalidateQueries({ queryKey: ['appointments', orgId] })
      setPendingDrop(null)
    },
    onError: () => {
      pendingDrop?.revert()
      setPendingDrop(null)
    },
  })

  const handleEventDrop = useCallback((arg: EventDropArg) => {
    if (!arg.event.start || !arg.event.end) {
      arg.revert()
      return
    }
    setPendingDrop(arg)
  }, [])

  const confirmDrop = () => {
    if (!pendingDrop?.event.start || !pendingDrop?.event.end) return
    updateMutation.mutate({
      id: pendingDrop.event.id,
      start: snapTo15(pendingDrop.event.start.getTime()),
      end: snapTo15(pendingDrop.event.end.getTime()),
    })
  }

  const cancelDrop = () => {
    pendingDrop?.revert()
    setPendingDrop(null)
  }

  // --- Event click ---------------------------------------------------------
  const handleEventClick = useCallback((arg: EventClickArg) => {
    setQueryStates({ calView: view, calDate: null })
    // Extend: open a detail modal by setting selectedEventId in URL state
    // e.g. setQueryStates({ selectedEventId: arg.event.id })
    const start = arg.event.start?.toLocaleString() ?? ''
    const end = arg.event.end?.toLocaleString() ?? ''
    const status = arg.event.extendedProps.status as string
    window.alert(`${arg.event.title}\nStatus: ${status}\n${start} → ${end}`)
  }, [view, setQueryStates])

  // --- Date select (click empty slot) ------------------------------------
  const handleDateSelect = useCallback(
    (arg: DateSelectArg) => {
      calRef.current?.getApi().unselect()
      onSelectDate?.(arg.start, arg.end)
    },
    [onSelectDate],
  )

  // --- Calendar navigation ------------------------------------------------
  const handleDatesSet = useCallback((arg: DatesSetArg) => {
    setRangeStart(arg.start.getTime())
    setRangeEnd(arg.end.getTime())
    setTitleText(arg.view.title)
  }, [])

  const navigate = (dir: 'prev' | 'next' | 'today') => {
    const api = calRef.current?.getApi()
    if (!api) return
    if (dir === 'today') api.today()
    else if (dir === 'prev') api.prev()
    else api.next()
  }

  const switchView = (v: CalendarViewType) => {
    setQueryStates({ calView: v })
    calRef.current?.getApi().changeView(v)
  }

  // --- Render -------------------------------------------------------------
  return (
    <div className="flex flex-col gap-3">
      {/* Custom toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1">
          <button
            onClick={() => navigate('prev')}
            className="rounded p-1.5 text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            onClick={() => navigate('today')}
            className="flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            <Calendar className="h-3.5 w-3.5" />
            Today
          </button>
          <button
            onClick={() => navigate('next')}
            className="rounded p-1.5 text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
          <span className="ml-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
            {titleText}
          </span>
          {isFetching && (
            <Loader2 className="ml-2 h-3.5 w-3.5 animate-spin text-slate-400" />
          )}
        </div>

        {/* View switcher */}
        <div className="flex items-center overflow-hidden rounded-md border border-slate-200 text-xs font-medium dark:border-slate-700">
          {VIEW_LABELS.map(([v, label]) => (
            <button
              key={v}
              onClick={() => switchView(v)}
              className={`px-3 py-1.5 transition-colors ${
                view === v
                  ? 'bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Drag-and-drop confirm banner */}
      {pendingDrop && (
        <div className="flex items-center justify-between gap-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm dark:border-amber-800 dark:bg-amber-950">
          <span className="text-amber-800 dark:text-amber-200">
            Reschedule <strong>{pendingDrop.event.title}</strong> to{' '}
            {pendingDrop.event.start?.toLocaleString()}?
          </span>
          <div className="flex gap-2">
            <Button variant="outline" onClick={cancelDrop} className="px-3 py-1 text-xs">
              Cancel
            </Button>
            <Button
              variant="accent"
              onClick={confirmDrop}
              disabled={updateMutation.isPending}
              className="px-3 py-1 text-xs"
            >
              {updateMutation.isPending ? 'Saving…' : 'Confirm'}
            </Button>
          </div>
        </div>
      )}

      {/* FullCalendar — key={view} forces re-render on view change to fix height bug */}
      <div className="relative rounded-lg border border-slate-200 bg-white p-2 dark:border-slate-700 dark:bg-slate-900 [&_.fc]:text-sm [&_.fc-toolbar]:hidden [&_.fc-event]:cursor-pointer [&_.fc-event]:rounded [&_.fc-daygrid-event]:text-xs">
        {isFetching && (
          <div className="pointer-events-none absolute inset-0 z-10 rounded-lg bg-white/50 dark:bg-slate-900/50" />
        )}
        <FullCalendar
          key={view}
          ref={calRef}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView={view}
          initialDate={calDate ?? undefined}
          headerToolbar={false}
          events={events}
          editable={true}
          selectable={true}
          selectMirror={true}
          dayMaxEvents={4}
          nowIndicator={true}
          height="auto"
          snapDuration="00:15:00"
          slotDuration="01:00:00"
          slotMinTime="06:00:00"
          slotMaxTime="22:00:00"
          allDaySlot={hasAllDay}
          datesSet={handleDatesSet}
          eventDrop={handleEventDrop}
          eventClick={handleEventClick}
          select={handleDateSelect}
        />
      </div>
    </div>
  )
}
