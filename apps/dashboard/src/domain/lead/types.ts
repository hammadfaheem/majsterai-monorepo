/** Lead domain types. */

export interface Lead {
  id: string
  org_id: string
  email: string | null
  phone: string | null
  name: string
  status: 'new' | 'contacted' | 'qualified' | 'converted' | 'lost'
  source: string | null
  last_inquiry_date: number | null
  last_contact_date: number | null
  created_at: number
  updated_at: number
}

export interface LeadCreate {
  name: string
  email?: string | null
  phone?: string | null
  source?: string | null
}

export interface LeadUpdate {
  name?: string | null
  email?: string | null
  phone?: string | null
  status?: string | null
  source?: string | null
}

export interface Note {
  id: string
  lead_id: string
  content: string
  created_at: number
  updated_at: number
}

export interface NoteCreate {
  content: string
}

export interface Activity {
  id: string
  lead_id: string
  type: string
  description: string
  created_at: number
}

export interface ActivityCreate {
  type: string
  description: string
}
