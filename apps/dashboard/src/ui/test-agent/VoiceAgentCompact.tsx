/** Compact VoiceAgent for the floating Test Agent widget. */

import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  VoiceAssistantControlBar,
  useRoomContext,
} from '@livekit/components-react'
import '@livekit/components-styles'
import { ConnectionState } from 'livekit-client'
import { useCallback, useState } from 'react'

interface VoiceAgentCompactProps {
  url: string
  token: string
  roomName: string
  onDisconnect?: () => void
}

function CompactRoomContent({ onDisconnect }: { onDisconnect?: () => void }) {
  const room = useRoomContext()
  const { state } = useVoiceAssistant()

  const handleDisconnect = useCallback(() => {
    room.disconnect()
    onDisconnect?.()
  }, [room, onDisconnect])

  const statusText =
    state === 'listening'
      ? 'Listening...'
      : state === 'speaking'
        ? 'Agent speaking...'
        : state === 'thinking'
          ? 'Thinking...'
          : 'Connected'

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Conversation / status area */}
      <div className="flex-1 min-h-[120px] overflow-y-auto rounded-lg bg-slate-800/50 border border-slate-700/50 p-3 mb-3">
        <div className="flex items-center gap-2 text-sm text-slate-300">
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              state === 'listening'
                ? 'bg-green-500 animate-pulse'
                : state === 'speaking'
                  ? 'bg-accent animate-pulse'
                  : 'bg-slate-500'
            }`}
          />
          {statusText}
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Conversation will appear here as you speak with the agent.
        </p>
      </div>

      {/* Controls: mic + end call */}
      <div className="flex items-center justify-center gap-3 pt-2 border-t border-slate-700/50">
        <VoiceAssistantControlBar />
        <button
          onClick={handleDisconnect}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors border border-red-500/40 text-sm font-medium"
        >
          End Call
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
        <CompactRoomContent onDisconnect={onDisconnect} />
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
