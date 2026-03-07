/** Floating minimizable Test Agent widget – Sophiie-style design with conversation, mic, end call. */

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { callService } from '@/application/call/callService'
import { useTestAgentWidgetStore } from '@/store/testAgentWidget.store'
import { VoiceAgentCompact } from './VoiceAgentCompact'
import { Button } from '@/ui/components/Button'
import { Mic, Minimize2, X, Loader2, AlertCircle, MessageCircle } from 'lucide-react'
import type { CreateRoomResponse } from '@/domain/call/types'

type CallState = 'idle' | 'loading' | 'connected' | 'error'

const AGENT_AVATAR_PLACEHOLDER = (
  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-accent to-accent/70 text-white text-sm font-semibold">
    AI
  </div>
)

export function TestAgentWidget() {
  const { currentOrganization } = useOrganization()
  const { isOpen, isMinimized, close, toggleMinimize } = useTestAgentWidgetStore()
  const [callState, setCallState] = useState<CallState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [roomData, setRoomData] = useState<CreateRoomResponse | null>(null)

  const agentName = currentOrganization?.name ?? 'Agent'

  const createRoomMutation = useMutation({
    mutationFn: (orgId: string) =>
      callService.createRoom({ org_id: orgId, mode: 'voice' }),
    onSuccess: (data) => {
      setRoomData(data)
      setCallState('connected')
    },
    onError: (err: Error) => {
      setError(err.message)
      setCallState('error')
    },
  })

  const handleStartCall = () => {
    if (!currentOrganization?.id) {
      setError('No organization found. Please complete onboarding.')
      setCallState('error')
      return
    }
    setCallState('loading')
    setError(null)
    createRoomMutation.mutate(currentOrganization.id)
  }

  const handleDisconnect = () => {
    setRoomData(null)
    setCallState('idle')
  }

  const handleClose = () => {
    if (callState === 'connected') {
      handleDisconnect()
    }
    close()
  }

  if (!isOpen) return null

  // Minimized: small floating bubble
  if (isMinimized) {
    return (
      <button
        onClick={toggleMinimize}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-accent text-white shadow-lg transition hover:bg-accent-light"
        aria-label="Expand Test Agent"
      >
        <Mic className="h-6 w-6" />
      </button>
    )
  }

  // Expanded: Sophiie-style panel
  return (
    <div
      className="fixed bottom-6 right-6 z-50 flex w-[400px] flex-col overflow-hidden rounded-2xl border border-slate-200/90 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900"
      role="dialog"
      aria-label="Test Agent"
    >
      {/* Header: avatar + title + controls */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-100 bg-slate-50/80 px-4 py-3 dark:border-slate-800 dark:bg-slate-800/40">
        <div className="flex items-center gap-3 min-w-0">
          {AGENT_AVATAR_PLACEHOLDER}
          <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
            Call with {agentName}
          </span>
        </div>
        <div className="flex items-center gap-0.5 shrink-0">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
            aria-label="Chat"
          >
            <MessageCircle className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={toggleMinimize}
            aria-label="Minimize"
          >
            <Minimize2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleClose}
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex min-h-[360px] flex-col p-4">
        {callState === 'idle' && (
          <div className="flex flex-1 flex-col items-center justify-center gap-5 py-6">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-700 shadow-inner">
              <span className="text-2xl font-bold text-slate-500 dark:text-slate-400">AI</span>
            </div>
            <div className="text-center space-y-1">
              <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">
                Test {agentName}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 max-w-[260px]">
                Check how your agent handles customer conversations.
              </p>
            </div>
            <Button
              onClick={handleStartCall}
              disabled={!currentOrganization?.id}
              variant="accent"
              size="lg"
              className="gap-2 rounded-xl"
            >
              <Mic className="h-4 w-4" />
              Start Call
            </Button>
          </div>
        )}

        {callState === 'loading' && (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 py-12">
            <Loader2 className="h-12 w-12 animate-spin text-accent" />
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Connecting to agent...
            </p>
          </div>
        )}

        {callState === 'connected' && roomData && (
          <VoiceAgentCompact
            url={roomData.url}
            token={roomData.token}
            roomName={roomData.room_name}
            agentName={agentName}
            onDisconnect={handleDisconnect}
          />
        )}

        {callState === 'error' && (
          <div className="flex flex-1 flex-col items-center justify-center gap-5 py-8">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
              <AlertCircle className="h-7 w-7 text-red-600 dark:text-red-400" />
            </div>
            <p className="text-center text-sm text-red-600 dark:text-red-400 px-4">
              {error}
            </p>
            <Button onClick={() => setCallState('idle')} variant="outline" size="default" className="rounded-lg">
              Try Again
            </Button>
          </div>
        )}
      </div>

      {/* Footer: Close Testing - when connected */}
      {callState === 'connected' && (
        <div className="border-t border-slate-100 dark:border-slate-800 px-4 py-2">
          <button
            onClick={handleClose}
            className="w-full text-center text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 py-1"
          >
            Close Testing
          </button>
        </div>
      )}
    </div>
  )
}
