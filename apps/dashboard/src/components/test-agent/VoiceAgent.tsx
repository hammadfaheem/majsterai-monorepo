"use client";

import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  BarVisualizer,
  VoiceAssistantControlBar,
  useRoomContext,
  useTracks,
} from "@livekit/components-react";
import "@livekit/components-styles";
import { Track, ConnectionState } from "livekit-client";
import { useCallback, useState } from "react";

interface VoiceAgentProps {
  url: string;
  token: string;
  roomName: string;
  onDisconnect?: () => void;
}

function AgentVisualizer() {
  const { state, audioTrack } = useVoiceAssistant();

  return (
    <div className="flex flex-col items-center justify-center gap-6">
      {/* Status Badge */}
      <div className="flex items-center gap-2">
        <span
          className={`w-2 h-2 rounded-full ${
            state === "listening"
              ? "bg-green-500 animate-pulse"
              : state === "speaking"
              ? "bg-accent animate-pulse"
              : "bg-slate-500"
          }`}
        />
        <span className="text-sm font-medium text-slate-300 capitalize">
          {state === "listening" ? "Listening..." : state === "speaking" ? "Speaking..." : state}
        </span>
      </div>

      {/* Audio Visualizer */}
      <div className="h-32 w-full max-w-md">
        <BarVisualizer
          state={state}
          barCount={7}
          trackRef={audioTrack}
          className="h-full"
          options={{
            minHeight: 20,
          }}
        />
      </div>
    </div>
  );
}

function RoomContent({ onDisconnect }: { onDisconnect?: () => void }) {
  const room = useRoomContext();
  const tracks = useTracks([Track.Source.Microphone]);

  const handleDisconnect = useCallback(() => {
    room.disconnect();
    onDisconnect?.();
  }, [room, onDisconnect]);

  return (
    <div className="flex flex-col items-center gap-8 p-8">
      {/* Agent Visualizer */}
      <AgentVisualizer />

      {/* Control Bar */}
      <div className="flex items-center gap-4">
        <VoiceAssistantControlBar />
        <button
          onClick={handleDisconnect}
          className="px-4 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition-colors border border-red-500/30"
        >
          End Call
        </button>
      </div>

      {/* Room Audio */}
      <RoomAudioRenderer />
    </div>
  );
}

export function VoiceAgent({ url, token, roomName, onDisconnect }: VoiceAgentProps) {
  const [connectionState, setConnectionState] = useState<ConnectionState>(
    ConnectionState.Disconnected
  );

  return (
    <LiveKitRoom
      serverUrl={url}
      token={token}
      connect={true}
      audio={true}
      video={false}
      onConnected={() => setConnectionState(ConnectionState.Connected)}
      onDisconnected={() => {
        setConnectionState(ConnectionState.Disconnected);
        onDisconnect?.();
      }}
      className="flex flex-col items-center justify-center"
    >
      {connectionState === ConnectionState.Connected ? (
        <RoomContent onDisconnect={onDisconnect} />
      ) : (
        <div className="flex items-center gap-3 text-slate-400">
          <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
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
          <span>Connecting to room...</span>
        </div>
      )}
    </LiveKitRoom>
  );
}
