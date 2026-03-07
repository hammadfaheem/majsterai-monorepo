/** Compact VoiceAgent for the floating Test Agent widget. */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  VoiceAssistantControlBar,
  useRoomContext,
  useLocalParticipant,
  useTranscriptions,
} from '@livekit/components-react'
import '@livekit/components-styles'
import { ConnectionState, RoomEvent } from 'livekit-client'
import type { TranscriptionSegment } from 'livekit-client'
import { PhoneOff } from 'lucide-react'

interface VoiceAgentCompactProps {
  url: string
  token: string
  roomName: string
  agentName?: string
  onDisconnect?: () => void
}

interface TranscriptEntry {
  id: string
  text: string
  role: 'user' | 'agent'
}

function CompactRoomContent({
  onDisconnect,
  agentName = 'Agent',
}: {
  onDisconnect?: () => void
  agentName?: string
}) {
  const room = useRoomContext()
  const { localParticipant } = useLocalParticipant()
  const { state } = useVoiceAssistant()
  const transcriptionsFromStream = useTranscriptions({ room })
  const scrollRef = useRef<HTMLDivElement>(null)
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([])
  const seenIds = useRef<Set<string>>(new Set())

  const handleDisconnect = useCallback(() => {
    room.disconnect()
    onDisconnect?.()
  }, [room, onDisconnect])

  // Subscribe to Room transcription events - captures BOTH user and agent speech
  useEffect(() => {
    const handler = (
      segments: TranscriptionSegment[],
      participant: { identity: string } | undefined
    ) => {
      if (!participant) return
      const isUser = participant.identity === localParticipant.identity
      const role: 'user' | 'agent' = isUser ? 'user' : 'agent'

      setTranscript((prev) => {
        const next = [...prev]
        for (const seg of segments) {
          if (seg.text && !seenIds.current.has(seg.id)) {
            seenIds.current.add(seg.id)
            next.push({ id: seg.id, text: seg.text, role })
          }
        }
        return next.slice(-100) // keep last 100 messages
      })
    }

    room.on(RoomEvent.TranscriptionReceived, handler)
    return () => {
      room.off(RoomEvent.TranscriptionReceived, handler)
    }
  }, [room, localParticipant.identity])

  // Merge RoomEvent transcript with useTranscriptions (lk.transcription streams)
  // useTranscriptions captures user speech when the agent forwards it
  const mergedTranscript = useMemo(() => {
    const fromStreams: TranscriptEntry[] = transcriptionsFromStream
      .filter((s) => s.text?.trim())
      .map((s, i) => ({
        id: `stream-${s.streamInfo.id}-${i}`,
        text: s.text,
        role: (s.participantInfo.identity === localParticipant.identity
          ? 'user'
          : 'agent') as 'user' | 'agent',
      }))

    const seen = new Set(transcript.map((e) => e.id))
    const combined = [...transcript]
    for (const e of fromStreams) {
      if (!seen.has(e.id)) {
        seen.add(e.id)
        combined.push(e)
      }
    }
    return combined.slice(-100)
  }, [transcript, transcriptionsFromStream, localParticipant.identity])

  // Auto-scroll when transcript updates
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [mergedTranscript])

  const statusText =
    state === 'listening'
      ? 'Listening...'
      : state === 'speaking'
        ? 'Speaking...'
        : state === 'thinking'
          ? 'Thinking...'
          : 'Connected'

  const displayTranscript = mergedTranscript
  const hasTranscripts = displayTranscript.length > 0

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Conversation area - scrollable transcript */}
      <div
        ref={scrollRef}
        className="flex-1 min-h-[160px] max-h-[220px] overflow-y-auto rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-700/80 p-3 mb-4 text-sm scrollbar-thin"
      >
        {/* Call started - always show when connected */}
        <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-3">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>Call started</span>
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-2">
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              state === 'listening'
                ? 'bg-green-500 animate-pulse'
                : state === 'speaking'
                  ? 'bg-accent animate-pulse'
                  : 'bg-slate-400'
            }`}
          />
          {statusText}
        </div>

        {/* Transcript messages - both You and Agent */}
        {hasTranscripts ? (
          <div className="space-y-2.5">
            {mergedTranscript.map((entry) => (
              <div
                key={entry.id}
                className={`rounded-lg px-3 py-2.5 shadow-sm ${
                  entry.role === 'user'
                    ? 'bg-accent/10 dark:bg-accent/20 border-l-2 border-accent ml-4 mr-0 text-slate-800 dark:text-slate-200'
                    : 'bg-white dark:bg-slate-800/80 border-l-2 border-slate-400 dark:border-slate-500 mr-4 ml-0 text-slate-700 dark:text-slate-200'
                }`}
              >
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400 block mb-0.5">
                  {entry.role === 'user' ? 'You' : agentName}
                </span>
                {entry.text}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-400 dark:text-slate-500 text-xs italic mt-1">
            Speak to start. Your messages and agent responses will appear here.
          </p>
        )}
      </div>

      {/* Controls: mic + end call */}
      <div className="flex items-center justify-center gap-4 pt-3 border-t border-slate-200 dark:border-slate-700">
        <VoiceAssistantControlBar />
        <button
          onClick={handleDisconnect}
          className="flex items-center justify-center gap-2 w-12 h-12 rounded-full bg-red-500 text-white hover:bg-red-600 transition-all shadow-lg hover:shadow-xl"
          aria-label="End call"
        >
          <PhoneOff className="h-5 w-5" />
        </button>
      </div>

      <RoomAudioRenderer />
    </div>
  )
}

export function VoiceAgentCompact({
  url,
  token,
  roomName: _roomName,
  agentName = 'Agent',
  onDisconnect,
}: VoiceAgentCompactProps) {
  const [connectionState, setConnectionState] = useState<ConnectionState>(
    ConnectionState.Disconnected
  )

  return (
    <LiveKitRoom
      serverUrl={url}
      token={token}
      connect={true}
      audio={true}
      video={false}
      onConnected={() => setConnectionState(ConnectionState.Connected)}
      onDisconnected={() => {
        setConnectionState(ConnectionState.Disconnected)
        onDisconnect?.()
      }}
      className="flex flex-col h-full min-h-0"
    >
      {connectionState === ConnectionState.Connected ? (
        <CompactRoomContent onDisconnect={onDisconnect} agentName={agentName} />
      ) : (
        <div className="flex items-center justify-center gap-2 py-6 text-slate-400 text-sm">
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Connecting...
        </div>
      )}
    </LiveKitRoom>
  )
}
