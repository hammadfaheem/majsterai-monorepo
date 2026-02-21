/** Agent config – edit AI agent name, prompt, variables. */

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { agentService } from '@/application/agent/agentService'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'

export function AgentConfigPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [prompt, setPrompt] = useState('')
  const [extraPrompt, setExtraPrompt] = useState('')
  const [variablesJson, setVariablesJson] = useState('{}')

  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', currentOrganization?.id],
    queryFn: () => agentService.getAgent(currentOrganization?.id ?? ''),
    enabled: !!currentOrganization?.id,
  })

  useEffect(() => {
    if (agent) {
      setName(agent.name)
      setPrompt(agent.prompt)
      setExtraPrompt(agent.extra_prompt ?? '')
      setVariablesJson(
        typeof agent.variables === 'object' && agent.variables != null
          ? JSON.stringify(agent.variables, null, 2)
          : '{}'
      )
    }
  }, [agent])

  const updateAgent = useMutation({
    mutationFn: () => {
      let variables: Record<string, unknown> | undefined
      try {
        variables = JSON.parse(variablesJson) as Record<string, unknown>
      } catch {
        variables = undefined
      }
      return agentService.updateAgent(currentOrganization!.id, {
        name: name || undefined,
        prompt: prompt || undefined,
        extra_prompt: extraPrompt || undefined,
        variables,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', currentOrganization?.id] })
    },
  })

  if (isLoading || !agent) {
    return (
      <div className="p-6">
        <p className="text-sm text-slate-500">Loading agent…</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Agent configuration</h1>
        <p className="mt-2 text-sm text-slate-600">
          Configure your voice AI agent
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Agent</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700">Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Agent name"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">System prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={6}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="Main system prompt"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Extra prompt</label>
            <textarea
              value={extraPrompt}
              onChange={(e) => setExtraPrompt(e.target.value)}
              rows={3}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="Additional context"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Variables (JSON)</label>
            <textarea
              value={variablesJson}
              onChange={(e) => setVariablesJson(e.target.value)}
              rows={4}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-sm"
              placeholder='{"key": "value"}'
            />
          </div>
          <Button
            variant="accent"
            onClick={() => updateAgent.mutate()}
            disabled={updateAgent.isPending}
          >
            {updateAgent.isPending ? 'Saving…' : 'Save'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
