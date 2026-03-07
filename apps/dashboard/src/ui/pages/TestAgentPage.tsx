import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { VoiceAgent } from '@/ui/test-agent/VoiceAgent'
import { callService } from '@/application/call/callService'
import { useOrganization } from '@/application/organization/organizationContext'
import {
  Card,
  CardContent,
} from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Mic, Loader2, AlertCircle, Settings } from 'lucide-react'
import type { CreateRoomResponse } from '@/domain/call/types'

type TestState = 'idle' | 'loading' | 'connected' | 'error'

export function TestAgentPage() {
  const { currentOrganization } = useOrganization()
  const [state, setState] = useState<TestState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [roomData, setRoomData] = useState<CreateRoomResponse | null>(null)

  // Create room mutation
  const createRoomMutation = useMutation({
    mutationFn: (orgId: string) =>
      callService.createRoom({ org_id: orgId, mode: 'voice' }),
    onSuccess: (data) => {
      setRoomData(data)
      setState('connected')
    },
    onError: (err: Error) => {
      setError(err.message)
      setState('error')
    },
  })

  // Start test call
  const handleStartCall = async () => {
    if (!currentOrganization?.id) {
      setError('No organization found. Please complete onboarding.')
      return
    }

    setState('loading')
    setError(null)
    createRoomMutation.mutate(currentOrganization.id)
  }

  // Handle disconnect
  const handleDisconnect = () => {
    setRoomData(null)
    setState('idle')
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">Test Agent</h1>
        <p className="text-slate-600">
          Start a voice conversation with your AI agent. Test prompts and configurations in real-time.
        </p>
      </div>

      {/* Call Interface */}
      <Card className="min-h-[400px]">
        {state === 'idle' && (
          <CardContent className="p-6">
            {/* Large white area with microphone icon */}
            <div className="bg-white dark:bg-slate-800/50 border-2 border-dashed border-slate-200 dark:border-slate-600 rounded-lg min-h-[300px] flex flex-col items-center justify-center mb-4">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                <Mic className="h-8 w-8 text-slate-400" />
              </div>
            </div>

            {/* Button and settings */}
            <div className="flex items-center justify-end gap-3">
              <Button
                onClick={handleStartCall}
                disabled={!currentOrganization?.id}
                variant="accent"
                size="default"
              >
                Start Testing
              </Button>
              <Button variant="ghost" size="icon">
                <Settings className="h-5 w-5" />
              </Button>
            </div>
          </CardContent>
        )}

        {state === 'loading' && (
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <Loader2 className="w-12 h-12 animate-spin text-accent mx-auto mb-4" />
              <p className="text-slate-600">Connecting to agent...</p>
            </div>
          </CardContent>
        )}

        {state === 'connected' && roomData && (
          <CardContent className="pt-6">
            <VoiceAgent
              url={roomData.url}
              token={roomData.token}
              roomName={roomData.room_name}
              onDisconnect={handleDisconnect}
            />
          </CardContent>
        )}

        {state === 'error' && (
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
              <p className="text-red-600 mb-4 font-medium">{error}</p>
              <Button onClick={() => setState('idle')} variant="outline">
                Try Again
              </Button>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Error Display */}
      {error && state !== 'error' && (
        <Card className="mt-4 border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600 text-sm">{error}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
