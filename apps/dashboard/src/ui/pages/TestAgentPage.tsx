import { useState, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { VoiceAgent } from '@/ui/test-agent/VoiceAgent'
import { callService } from '@/application/call/callService'
import { organizationService } from '@/application/organization/organizationService'
import { useOrganization } from '@/application/organization/organizationContext'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Mic, Loader2, AlertCircle, Plus, Settings } from 'lucide-react'
import type { CreateRoomResponse } from '@/domain/call/types'

type TestState = 'idle' | 'loading' | 'connected' | 'error'

export function TestAgentPage() {
  const { organizations, currentOrganization, setCurrentOrganization } =
    useOrganization()
  const [state, setState] = useState<TestState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [roomData, setRoomData] = useState<CreateRoomResponse | null>(null)
  const [selectedOrgId, setSelectedOrgId] = useState<string>('')
  const [newOrgName, setNewOrgName] = useState('')
  const [showCreateOrg, setShowCreateOrg] = useState(false)

  // Set selected org from current organization
  useEffect(() => {
    if (currentOrganization) {
      setSelectedOrgId(currentOrganization.id)
    }
  }, [currentOrganization])

  // Create organization mutation
  const createOrgMutation = useMutation({
    mutationFn: (name: string) =>
      organizationService.createOrganization({ name }),
    onSuccess: (org) => {
      setCurrentOrganization(org)
      setSelectedOrgId(org.id)
      setNewOrgName('')
      setShowCreateOrg(false)
    },
    onError: (err: Error) => {
      setError(err.message)
    },
  })

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

  // Create new organization
  const handleCreateOrg = async () => {
    if (!newOrgName.trim()) return
    createOrgMutation.mutate(newOrgName.trim())
  }

  // Start test call
  const handleStartCall = async () => {
    if (!selectedOrgId) {
      setError('Please select or create an organization first')
      return
    }

    setState('loading')
    setError(null)
    createRoomMutation.mutate(selectedOrgId)
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

      {/* Organization Selection */}
      {state === 'idle' && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Select Organization</CardTitle>
            <CardDescription>
              Choose an organization to test your agent with
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {organizations.length > 0 ? (
              <>
                <select
                  value={selectedOrgId}
                  onChange={(e) => {
                    setSelectedOrgId(e.target.value)
                    const org = organizations.find((o) => o.id === e.target.value)
                    if (org) setCurrentOrganization(org)
                  }}
                  className="flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
                >
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowCreateOrg(!showCreateOrg)}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create new organization
                </Button>
              </>
            ) : (
              <p className="text-slate-500 text-sm">
                No organizations yet. Create one to get started.
              </p>
            )}

            {/* Create Organization Form */}
            {(showCreateOrg || organizations.length === 0) && (
              <div className="flex gap-3 pt-4 border-t">
                <Input
                  type="text"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  placeholder="Organization name..."
                  className="flex-1"
                />
                <Button
                  onClick={handleCreateOrg}
                  disabled={!newOrgName.trim() || createOrgMutation.isPending}
                  variant="accent"
                >
                  {createOrgMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create'
                  )}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

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
                disabled={!selectedOrgId && organizations.length > 0}
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
