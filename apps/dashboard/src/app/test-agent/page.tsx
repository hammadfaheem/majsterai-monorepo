"use client";

import Link from "next/link";
import { useState, useCallback, useEffect } from "react";
import { VoiceAgent } from "@/components/test-agent/VoiceAgent";
import { createRoom, createOrganization, listOrganizations, type Organization, type CreateRoomResponse } from "@/lib/api";

type TestState = "idle" | "loading" | "connected" | "error";

export default function TestAgentPage() {
  const [state, setState] = useState<TestState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [roomData, setRoomData] = useState<CreateRoomResponse | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState<string>("");
  const [newOrgName, setNewOrgName] = useState("");
  const [showCreateOrg, setShowCreateOrg] = useState(false);

  // Load organizations on mount
  const loadOrganizations = useCallback(async () => {
    try {
      const orgs = await listOrganizations();
      setOrganizations(orgs);
      if (orgs.length > 0 && !selectedOrgId) {
        setSelectedOrgId(orgs[0].id);
      }
    } catch (err) {
      console.error("Failed to load organizations:", err);
    }
  }, [selectedOrgId]);

  // Create new organization
  const handleCreateOrg = async () => {
    if (!newOrgName.trim()) return;
    
    try {
      const org = await createOrganization(newOrgName);
      setOrganizations((prev) => [org, ...prev]);
      setSelectedOrgId(org.id);
      setNewOrgName("");
      setShowCreateOrg(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create organization");
    }
  };

  // Start test call
  const handleStartCall = async () => {
    if (!selectedOrgId) {
      setError("Please select or create an organization first");
      return;
    }

    setState("loading");
    setError(null);

    try {
      const data = await createRoom(selectedOrgId, "voice");
      setRoomData(data);
      setState("connected");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start call");
      setState("error");
    }
  };

  // Handle disconnect
  const handleDisconnect = () => {
    setRoomData(null);
    setState("idle");
  };

  // Load orgs on component mount
  useEffect(() => {
    loadOrganizations();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 backdrop-blur bg-slate-900/50 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-white">
            Majster<span className="text-accent">AI</span>
          </Link>
          <span className="text-sm text-slate-400">Test Agent</span>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          {/* Title */}
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold text-white mb-3">Test Your Agent</h1>
            <p className="text-slate-400">
              Start a voice conversation with your AI agent
            </p>
          </div>

          {/* Organization Selection */}
          {state === "idle" && (
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-6 mb-8">
              <h2 className="text-lg font-semibold text-white mb-4">Select Organization</h2>
              
              {organizations.length > 0 ? (
                <div className="space-y-4">
                  <select
                    value={selectedOrgId}
                    onChange={(e) => setSelectedOrgId(e.target.value)}
                    className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-accent"
                  >
                    {organizations.map((org) => (
                      <option key={org.id} value={org.id}>
                        {org.name}
                      </option>
                    ))}
                  </select>
                  
                  <button
                    onClick={() => setShowCreateOrg(!showCreateOrg)}
                    className="text-sm text-accent hover:text-accent-light"
                  >
                    + Create new organization
                  </button>
                </div>
              ) : (
                <p className="text-slate-400 mb-4">No organizations yet. Create one to get started.</p>
              )}

              {/* Create Organization Form */}
              {(showCreateOrg || organizations.length === 0) && (
                <div className="mt-4 flex gap-3">
                  <input
                    type="text"
                    value={newOrgName}
                    onChange={(e) => setNewOrgName(e.target.value)}
                    placeholder="Organization name..."
                    className="flex-1 bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-accent"
                  />
                  <button
                    onClick={handleCreateOrg}
                    disabled={!newOrgName.trim()}
                    className="px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent-light disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Create
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Call Interface */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
            {state === "idle" && (
              <div className="text-center">
                <div className="w-24 h-24 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg
                    className="w-12 h-12 text-accent"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  </svg>
                </div>
                <button
                  onClick={handleStartCall}
                  disabled={!selectedOrgId && organizations.length > 0}
                  className="px-8 py-4 bg-accent text-white text-lg font-semibold rounded-xl hover:bg-accent-light disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-accent/25 hover:shadow-accent/40"
                >
                  Start Voice Call
                </button>
                <p className="mt-4 text-sm text-slate-500">
                  Make sure your microphone is enabled
                </p>
              </div>
            )}

            {state === "loading" && (
              <div className="text-center py-12">
                <svg className="w-12 h-12 animate-spin text-accent mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <p className="text-slate-400">Connecting to agent...</p>
              </div>
            )}

            {state === "connected" && roomData && (
              <VoiceAgent
                url={roomData.url}
                token={roomData.token}
                roomName={roomData.room_name}
                onDisconnect={handleDisconnect}
              />
            )}

            {state === "error" && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <p className="text-red-400 mb-4">{error}</p>
                <button
                  onClick={() => setState("idle")}
                  className="px-6 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>

          {/* Error Display */}
          {error && state !== "error" && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
