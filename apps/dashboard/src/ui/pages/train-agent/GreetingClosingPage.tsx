/** Greeting and Closing – configure greeting, after-hours, and closing messages for phone calls. */

import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { agentService } from '@/application/agent/agentService'
import { organizationService } from '@/application/organization/organizationService'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Phone, Volume2, Check, AlertCircle, X } from 'lucide-react'
import { cn } from '@/lib/utils'

const VARIABLES = [
  { key: 'customer_first_name', label: 'Customer First Name', description: "Customer's first name" },
  { key: 'customer_last_name', label: 'Customer Last Name', description: "Customer's last name" },
  { key: 'business_name', label: 'Business Name', description: 'Your business name' },
  { key: 'agent_name', label: 'Agent Name', description: 'AI agent name' },
]

type MessageSegment = { type: 'text'; value: string } | { type: 'variable'; key: string }

function parseMessageToSegments(str: string): MessageSegment[] {
  if (!str.trim()) return [{ type: 'text', value: '' }]
  const regex = /\{\{([^}]+)\}\}/g
  const segments: MessageSegment[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null
  while ((match = regex.exec(str)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: 'text', value: str.slice(lastIndex, match.index) })
    }
    segments.push({ type: 'variable', key: match[1].trim() })
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < str.length) {
    segments.push({ type: 'text', value: str.slice(lastIndex) })
  }
  if (segments.length === 0) segments.push({ type: 'text', value: str })
  return segments
}

function segmentsToMessage(segments: MessageSegment[]): string {
  return segments
    .map((s) => (s.type === 'text' ? s.value : `{{${s.key}}}`))
    .join('')
}

function getVariableLabel(key: string): string {
  return VARIABLES.find((v) => v.key === key)?.label ?? key.replace(/_/g, ' ')
}

interface VariableMessageInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  businessName: string
  agentName: string
}

function VariableMessageInput({
  value,
  onChange,
  placeholder = 'Enter your message...',
  businessName,
  agentName,
}: VariableMessageInputProps) {
  const segments = parseMessageToSegments(value)

  const updateSegment = (index: number, newValue: string) => {
    const seg = segments[index]
    if (seg.type !== 'text') return
    const next = [...segments]
    next[index] = { type: 'text', value: newValue }
    onChange(segmentsToMessage(next))
  }

  const removeVariable = (index: number) => {
    const next = segments.filter((_, i) => i !== index)
    onChange(segmentsToMessage(next))
  }

  const insertVariable = (key: string) => {
    onChange(value + `{{${key}}}`)
  }

  return (
    <div className="space-y-2">
      <div className="min-h-[56px] rounded-lg border border-slate-300 bg-white p-2 dark:border-slate-600 dark:bg-slate-800">
        <div className="flex flex-wrap items-baseline gap-0">
          {segments.map((seg, i) =>
            seg.type === 'text' ? (
              <input
                key={i}
                type="text"
                value={seg.value}
                onChange={(e) => updateSegment(i, e.target.value)}
                placeholder={segments.length === 1 && !seg.value ? placeholder : undefined}
                size={Math.max(1, Math.floor(seg.value.length * 0.75))}
                className="m-0 min-w-[2ch] shrink-0 border-0 bg-transparent p-0 text-sm outline-none placeholder:text-slate-400 focus:ring-0 dark:text-slate-100"
              />
            ) : (
              <span
                key={i}
                className="inline-flex items-center gap-0.5 rounded bg-blue-100 px-1 py-px text-sm font-medium text-blue-800 dark:bg-blue-900/40 dark:text-blue-200"
              >
                {getVariableLabel(seg.key)}
                <button
                  type="button"
                  onClick={() => removeVariable(i)}
                  className="rounded p-0.5 hover:bg-blue-200/50 dark:hover:bg-blue-800/50"
                  aria-label={`Remove ${getVariableLabel(seg.key)}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            )
          )}
        </div>
      </div>
      <div>
        <p className="mb-2 text-xs font-medium text-slate-500 dark:text-slate-400">Add Variables:</p>
        <div className="flex flex-wrap gap-2">
          {VARIABLES.map((v) => (
            <button
              key={v.key}
              type="button"
              onClick={() => insertVariable(v.key)}
              className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              {v.label}
            </button>
          ))}
        </div>
        <div className="mt-1.5 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-400 dark:text-slate-500 sm:grid-cols-4">
          {VARIABLES.map((v) => (
            <span key={v.key}>
              {v.label}: {v.key === 'business_name' ? businessName : v.key === 'agent_name' ? agentName : v.description}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

const RECORDING_KEYWORDS = ['recorded', 'recording']

function hasRecordingDisclosure(text: string): boolean {
  const lower = text.toLowerCase()
  return RECORDING_KEYWORDS.some((kw) => lower.includes(kw))
}

interface GreetingClosingSettings {
  phone?: {
    greeting_enabled?: boolean
    greeting_message?: string
    greeting_delay?: number
    after_hours_enabled?: boolean
    after_hours_message?: string
    after_hours_delay?: number
    closing_message?: string
  }
}

const DEFAULT_GREETING =
  "Hello! This is {{agent_name}}, a digital assistant for {{business_name}} on a recorded line. How can I help you?"
const DEFAULT_AFTER_HOURS =
  "Hello! This is {{agent_name}}, a digital assistant. You've reached {{business_name}} after hours, and this call is on a recorded line. How can I help you today?"
const DEFAULT_CLOSING = 'Thank you for calling {{business_name}}. Have a great day!'

function getGreetingClosing(settings: Record<string, unknown> | null | undefined): GreetingClosingSettings {
  const gc = settings?.greeting_closing as Record<string, unknown> | undefined
  if (!gc) return {}
  const phone = gc.phone as Record<string, unknown> | undefined
  return {
    phone: phone
      ? {
          greeting_enabled: phone.greeting_enabled as boolean | undefined,
          greeting_message: phone.greeting_message as string | undefined,
          greeting_delay: (phone.greeting_delay as number) ?? 0,
          after_hours_enabled: phone.after_hours_enabled as boolean | undefined,
          after_hours_message: phone.after_hours_message as string | undefined,
          after_hours_delay: (phone.after_hours_delay as number) ?? 0,
          closing_message: phone.closing_message as string | undefined,
        }
      : undefined,
  }
}

interface MessageBlockProps {
  title: string
  description?: string
  enabled?: boolean
  onEnabledChange?: (v: boolean) => void
  message: string
  onMessageChange: (v: string) => void
  showRecordingDisclosure?: boolean
  delay?: number
  onDelayChange?: (v: number) => void
  delayLabel?: string
  businessName: string
  agentName: string
}

function MessageBlock({
  title,
  description,
  enabled = true,
  onEnabledChange,
  message,
  onMessageChange,
  showRecordingDisclosure = false,
  delay = 0,
  onDelayChange,
  delayLabel = 'Welcome Message Delay',
  businessName,
  agentName,
}: MessageBlockProps) {
  const disclosureValid = showRecordingDisclosure ? hasRecordingDisclosure(message) : true

  const previewText = message
    .replace(/\{\{customer_first_name\}\}/g, 'John')
    .replace(/\{\{customer_last_name\}\}/g, 'Doe')
    .replace(/\{\{business_name\}\}/g, businessName || 'Hammad Org')
    .replace(/\{\{agent_name\}\}/g, agentName || 'Sophiie')

  return (
    <div className="space-y-4 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-medium text-slate-900 dark:text-slate-100">{title}</h4>
          {description && (
            <p className="text-sm text-slate-500 dark:text-slate-400">{description}</p>
          )}
        </div>
        {onEnabledChange != null && (
          <label className="relative inline-flex cursor-pointer items-center">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => onEnabledChange(e.target.checked)}
              className="peer sr-only"
            />
            <div
              className={cn(
                'relative h-6 w-11 shrink-0 rounded-full transition-colors',
                enabled ? 'bg-accent' : 'bg-slate-200 dark:bg-slate-600'
              )}
            >
              <div
                className={cn(
                  'absolute left-1 top-1 h-4 w-4 rounded-full bg-white shadow transition-transform',
                  enabled && 'translate-x-5'
                )}
              />
            </div>
          </label>
        )}
      </div>

      {(!onEnabledChange || enabled) && (
        <>
          <div>
            <VariableMessageInput
              value={message}
              onChange={onMessageChange}
              businessName={businessName}
              agentName={agentName}
            />
          </div>

          {showRecordingDisclosure && (
            <div className="flex items-center gap-2">
              {disclosureValid ? (
                <>
                  <Check className="h-4 w-4 text-emerald-500" />
                  <span className="text-sm text-emerald-600 dark:text-emerald-400">
                    Call Recording Disclosure – Valid
                  </span>
                </>
              ) : (
                <>
                  <AlertCircle className="h-4 w-4 text-amber-500" />
                  <span className="text-sm text-amber-600 dark:text-amber-400">
                    Call Recording Disclosure – Missing. In order for call recording to be active,
                    recording disclosure must be included.
                  </span>
                </>
              )}
            </div>
          )}

          {onDelayChange != null && (
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                {delayLabel}
              </label>
              <p className="text-xs text-slate-500">
                Delay before playing the welcome message (in seconds)
              </p>
              <div className="mt-1 flex items-center gap-2">
                <input
                  type="range"
                  min={0}
                  max={5}
                  step={0.5}
                  value={delay}
                  onChange={(e) => onDelayChange(parseFloat(e.target.value))}
                  className="h-2 w-32 flex-1 max-w-[200px] rounded-full accent-accent"
                />
                <span className="text-sm text-slate-600 dark:text-slate-400">
                  {delay.toFixed(1)}s
                </span>
              </div>
            </div>
          )}

          <div className="flex items-center gap-2">
            <Button type="button" variant="outline" size="sm" className="gap-1">
              <Volume2 className="h-4 w-4" />
              Preview Audio
            </Button>
            <span className="text-xs text-slate-500 italic">Preview: "{previewText}"</span>
          </div>
        </>
      )}
    </div>
  )
}

export function GreetingClosingPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''

  const { data: agent, isLoading: agentLoading } = useQuery({
    queryKey: ['agent', orgId],
    queryFn: () => agentService.getAgent(orgId),
    enabled: !!orgId,
  })

  const { data: orgData } = useQuery({
    queryKey: ['organization', orgId],
    queryFn: () => organizationService.getOrganization(orgId),
    enabled: !!orgId,
  })

  const org = orgData ?? (currentOrganization as { name?: string } | null)
  const businessName = (org?.name as string) ?? 'Hammad Org'
  const agentName = (agent?.name as string) ?? 'Sophiie'

  const settings = getGreetingClosing(agent?.settings ?? null)

  const [phoneGreetingEnabled, setPhoneGreetingEnabled] = useState(true)
  const [phoneGreetingMessage, setPhoneGreetingMessage] = useState(DEFAULT_GREETING)
  const [phoneGreetingDelay, setPhoneGreetingDelay] = useState(0)
  const [phoneAfterHoursEnabled, setPhoneAfterHoursEnabled] = useState(true)
  const [phoneAfterHoursMessage, setPhoneAfterHoursMessage] = useState(DEFAULT_AFTER_HOURS)
  const [phoneAfterHoursDelay, setPhoneAfterHoursDelay] = useState(0)
  const [phoneClosingMessage, setPhoneClosingMessage] = useState(DEFAULT_CLOSING)

  useEffect(() => {
    const p = settings.phone
    if (p) {
      if (p.greeting_enabled !== undefined) setPhoneGreetingEnabled(p.greeting_enabled)
      if (p.greeting_message) setPhoneGreetingMessage(p.greeting_message)
      if (p.greeting_delay != null) setPhoneGreetingDelay(p.greeting_delay)
      if (p.after_hours_enabled !== undefined) setPhoneAfterHoursEnabled(p.after_hours_enabled)
      if (p.after_hours_message) setPhoneAfterHoursMessage(p.after_hours_message)
      if (p.after_hours_delay != null) setPhoneAfterHoursDelay(p.after_hours_delay)
      if (p.closing_message) setPhoneClosingMessage(p.closing_message)
    }
  }, [agent?.settings])

  const updateAgent = useMutation({
    mutationFn: () => {
      const current = (agent?.settings ?? {}) as Record<string, unknown>
      const greeting_closing: GreetingClosingSettings = {
        phone: {
          greeting_enabled: phoneGreetingEnabled,
          greeting_message: phoneGreetingMessage,
          greeting_delay: phoneGreetingDelay,
          after_hours_enabled: phoneAfterHoursEnabled,
          after_hours_message: phoneAfterHoursMessage,
          after_hours_delay: phoneAfterHoursDelay,
          closing_message: phoneClosingMessage,
        },
      }
      return agentService.updateAgent(orgId, {
        settings: { ...current, greeting_closing },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', orgId] })
    },
  })

  if (agentLoading || !agent) {
    return (
      <div className="text-slate-600 dark:text-slate-400">Loading agent configuration…</div>
    )
  }

  if (!currentOrganization) {
    return (
      <div className="text-slate-600 dark:text-slate-400">
        Select an organization to configure greeting and closing messages.
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
          Greeting and Closing
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Configure what your agent says when answering calls, after hours, and when closing conversations.
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          updateAgent.mutate()
        }}
        className="space-y-8"
      >
        {/* Phone Calls */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Phone className="h-5 w-5 text-slate-500" />
            <CardTitle>Phone Calls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <MessageBlock
              title="Greeting Message"
              description="The first thing your agent says when answering a call."
              enabled={phoneGreetingEnabled}
              onEnabledChange={setPhoneGreetingEnabled}
              message={phoneGreetingMessage}
              onMessageChange={setPhoneGreetingMessage}
              showRecordingDisclosure
              delay={phoneGreetingDelay}
              onDelayChange={setPhoneGreetingDelay}
              delayLabel="Welcome Message Delay"
              businessName={businessName}
              agentName={agentName}
            />

            <MessageBlock
              title="After Hours Message"
              description="Played when a call is received outside of business hours."
              enabled={phoneAfterHoursEnabled}
              onEnabledChange={setPhoneAfterHoursEnabled}
              message={phoneAfterHoursMessage}
              onMessageChange={setPhoneAfterHoursMessage}
              showRecordingDisclosure
              delay={phoneAfterHoursDelay}
              onDelayChange={setPhoneAfterHoursDelay}
              delayLabel="After-Hours Welcome Message Delay"
              businessName={businessName}
              agentName={agentName}
            />

            <MessageBlock
              title="Closing Message"
              description="What your agent says before hanging up."
              message={phoneClosingMessage}
              onMessageChange={setPhoneClosingMessage}
              businessName={businessName}
              agentName={agentName}
            />
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" variant="accent" disabled={updateAgent.isPending}>
            {updateAgent.isPending ? 'Saving…' : 'Save changes'}
          </Button>
        </div>
      </form>
    </div>
  )
}
