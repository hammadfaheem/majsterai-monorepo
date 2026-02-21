/** Membership domain types. */

export interface Membership {
  id: string
  org_id: string
  user_id: string
  role: 'owner' | 'admin' | 'member'
  created_at: number
  updated_at: number
}

export interface AddMemberRequest {
  user_id: string
  role?: string
  invited_email?: string | null
  scheduling_priority?: number | null
  responsibility?: string | null
  personalisation_notes?: string | null
  is_point_of_escalation?: boolean
}

export interface UpdateMemberRoleRequest {
  role?: string
  is_disabled?: boolean | null
  is_point_of_escalation?: boolean | null
  scheduling_priority?: number | null
  responsibility?: string | null
  personalisation_notes?: string | null
}
