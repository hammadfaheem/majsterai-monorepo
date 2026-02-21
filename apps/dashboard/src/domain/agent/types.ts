export interface Agent {
  id: number
  org_id: string
  name: string
  prompt: string
  extra_prompt: string | null
  is_custom_prompt: boolean
  llm_model: string
  stt_model: string
  tts_model: Record<string, unknown> | null
  settings: Record<string, unknown> | null
  variables: Record<string, unknown> | null
  status: string
  created_at?: number
  updated_at?: number
}

export interface UpdateAgentRequest {
  name?: string
  prompt?: string
  extra_prompt?: string | null
  is_custom_prompt?: boolean
  llm_model?: string
  stt_model?: string
  tts_model?: Record<string, unknown> | null
  settings?: Record<string, unknown> | null
  variables?: Record<string, unknown> | null
}
