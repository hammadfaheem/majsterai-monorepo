import { apiClient } from '@/infrastructure/api'
import type {
  CreateRoomRequest,
  CreateRoomResponse,
} from '@/domain/call/types'

export class CallService {
  async createRoom(data: CreateRoomRequest): Promise<CreateRoomResponse> {
    const response = await apiClient.post<CreateRoomResponse>(
      '/api/livekit/create-room',
      data
    )
    return response.data
  }
}

export const callService = new CallService()
