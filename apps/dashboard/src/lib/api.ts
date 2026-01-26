/**
 * API client for MajsterAI backend
 */

// Use environment variable or default to localhost for development
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface CreateRoomResponse {
  room_name: string;
  url: string;
  token: string;
  metadata: Record<string, unknown>;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  time_zone: string;
  country: string | null;
  currency: string;
  created_at: number;
}

export interface Agent {
  id: number;
  org_id: string;
  name: string;
  prompt: string;
  extra_prompt: string | null;
  is_custom_prompt: boolean;
  llm_model: string;
  stt_model: string;
  tts_model: Record<string, unknown> | null;
  settings: Record<string, unknown> | null;
  status: string;
}

/**
 * Create a LiveKit room for testing the agent
 */
export async function createRoom(orgId: string, mode: "voice" | "text" = "voice"): Promise<CreateRoomResponse> {
  const response = await fetch(`${API_BASE}/livekit/create-room`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ org_id: orgId, mode }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create room");
  }

  return response.json();
}

/**
 * Create a new organization
 */
export async function createOrganization(name: string): Promise<Organization> {
  const response = await fetch(`${API_BASE}/organizations/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create organization");
  }

  return response.json();
}

/**
 * List all organizations
 */
export async function listOrganizations(): Promise<Organization[]> {
  const response = await fetch(`${API_BASE}/organizations/`);

  if (!response.ok) {
    throw new Error("Failed to fetch organizations");
  }

  return response.json();
}

/**
 * Get agent configuration for an organization
 */
export async function getAgent(orgId: string): Promise<Agent> {
  const response = await fetch(`${API_BASE}/agents/${orgId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch agent");
  }

  return response.json();
}

/**
 * Update agent configuration
 */
export async function updateAgent(orgId: string, data: Partial<Agent>): Promise<Agent> {
  const response = await fetch(`${API_BASE}/agents/${orgId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update agent");
  }

  return response.json();
}
