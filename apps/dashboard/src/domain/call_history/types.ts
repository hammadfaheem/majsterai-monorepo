/** Call history domain types. */

export interface CallHistory {
  id: number
  room_name: string
  org_id: string
  agent_id: number | null
  direction: 'inbound' | 'outbound' | 'web'
  from_phone_number: string | null
  to_phone_number: string | null
  start_time: number | null
  end_time: number | null
  duration: number | null
  status: 'pending' | 'active' | 'completed'
  summary: string | null
  created_at: number
  updated_at: number
}

export interface Transcript {
  id: string
  room_name: string
  org_id: string
  transcript: string
  segments: Record<string, unknown> | null
  sentiment: 'positive' | 'neutral' | 'negative' | null
  keywords: string[] | null
  summary: string | null
  created_at: number
  updated_at: number
}

export interface CallDetails {
  call_history: CallHistory
  transcript: Transcript | null
}

export interface CallAnalytics {
  total_calls: number
  completed_calls: number
  average_duration_seconds: number
  total_duration_seconds: number
}
