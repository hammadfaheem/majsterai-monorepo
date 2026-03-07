/** Floating minimizable Test Agent widget – conversation, mic, end call. */

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { callService } from '@/application/call/callService'
import { useTestAgentWidgetStore } from '@/store/testAgentWidget.store'
import { VoiceAgentCompact } from './VoiceAgentCompact'
import { Button } from '@/ui/components/Button'
import { Mic, Minimize2, X, Loader2, AlertCircle } from 'lucide-react'
import type { CreateRoomResponse } from '@/domain/call/types'

type CallState = 'idle' | 'loading' | 'connected' | 'error'

export function TestAgentWidget() {
  const { currentOrganization } = useOrganization()
  const { isOpen, isMinimized, close, toggleMinimize } = useTestAgentWidgetStore()
  const [callState, setCallState] = useState<CallState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [roomData, setRoomData] = useState<CreateRoomResponse | null>(null)

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

  // Expanded: full panel
  return (
    <div
      className="fixed bottom-6 right-6 z-50 flex w-[380px] flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl dark:border-slate-700 dark:bg-slate-900"
      role="dialog"
      aria-label="Test Agent"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-800/50">
        <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
          Test Agent
        </span>
        <div className="flex items-center gap-1">
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
      <div className="flex min-h-[320px] flex-col p-4">
        {callState === 'idle' && (
          <div className="flex flex-1 flex-col items-center justify-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
              <Mic className="h-8 w-8 text-slate-400" />
            </div>
            <p className="text-center text-sm text-slate-500 dark:text-slate-400">
              Start a voice conversation with your AI agent
            </p>
            <Button
              onClick={handleStartCall}
              disabled={!currentOrganization?.id}
              variant="accent"
              size="default"
              className="gap-2"
            >
              <Mic className="h-4 w-4" />
              Start Call
            </Button>
          </div>
        )}

        {callState === 'loading' && (
          <div className="flex flex-1 flex-col items-center justify-center gap-3">
            <Loader2 className="h-10 w-10 animate-spin text-accent" />
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Connecting...
            </p>
          </div>
        )}

        {callState === 'connected' && roomData && (
          <VoiceAgentCompact
            url={roomData.url}
            token={roomData.token}
            roomName={roomData.room_name}
            onDisconnect={handleDisconnect}
          />
        )}

        {callState === 'error' && (
          <div className="flex flex-1 flex-col items-center justify-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
              <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <p className="text-center text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
            <Button onClick={() => setCallState('idle')} variant="outline" size="sm">
              Try Again
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
