import { create } from 'zustand'

const THEME_STORAGE_KEY = 'majsterai-theme'

function getStoredTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light'
  const stored = localStorage.getItem(THEME_STORAGE_KEY) as 'light' | 'dark' | null
  return stored === 'dark' || stored === 'light' ? stored : 'light'
}

interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setTheme: (theme: 'light' | 'dark') => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  theme: getStoredTheme(),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setTheme: (theme) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(THEME_STORAGE_KEY, theme)
    }
    set({ theme })
  },
}))
