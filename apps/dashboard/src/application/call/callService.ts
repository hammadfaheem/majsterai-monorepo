import { apiClient } from '@/infrastructure/api'
import type {
  CreateRoomRequest,
  CreateRoomResponse,
} from '@/domain/call/types'

export class CallService {
  /**
   * Create a LiveKit room for testing the agent
   */
  async createRoom(data: CreateRoomRequest): Promise<CreateRoomResponse> {
    const response = await apiClient.post<CreateRoomResponse>(
      '/api/livekit/create-room',
      data
    )
    return response.data
  }

  /**
   * Generate a participant token for an existing room
   */
  async generateToken(
    roomName: string,
    participantName: string,
    orgId: string
  ): Promise<{ token: string }> {
    const response = await apiClient.post<{ token: string }>('/api/livekit/token', {
      room_name: roomName,
      participant_name: participantName,
      org_id: orgId,
    })
    return response.data
  }
}

export const callService = new CallService()
