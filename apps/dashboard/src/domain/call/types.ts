export interface CreateRoomResponse {
  room_name: string
  url: string
  token: string
  metadata: Record<string, unknown>
}

export interface CreateRoomRequest {
  org_id: string
  mode?: 'voice' | 'text'
}
