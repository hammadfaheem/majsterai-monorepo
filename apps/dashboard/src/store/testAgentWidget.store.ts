import { create } from 'zustand'

interface TestAgentWidgetState {
  isOpen: boolean
  isMinimized: boolean
  open: () => void
  close: () => void
  toggleMinimize: () => void
  toggle: () => void
}

export const useTestAgentWidgetStore = create<TestAgentWidgetState>((set) => ({
  isOpen: false,
  isMinimized: false,
  open: () => set({ isOpen: true, isMinimized: false }),
  close: () => set({ isOpen: false, isMinimized: false }),
  toggleMinimize: () => set((s) => ({ isMinimized: !s.isMinimized })),
  toggle: () => set((s) => ({ isOpen: !s.isOpen, isMinimized: s.isOpen ? s.isMinimized : false })),
}))
