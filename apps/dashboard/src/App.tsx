import { useEffect } from 'react'
import { Provider } from 'react-redux'
import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { store } from './store'
import { queryClient } from './lib/react-query'
import { useUIStore } from './store/ui.store'
import { AuthInit } from './ui/components/AuthInit'
import { OrganizationProvider } from './application/organization/organizationContext'
import { Router } from './router'

function ThemeSync() {
  const theme = useUIStore((s) => s.theme)
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])
  return null
}

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ThemeSync />
          <AuthInit>
            <OrganizationProvider>
              <Router />
            </OrganizationProvider>
          </AuthInit>
        </BrowserRouter>
      </QueryClientProvider>
    </Provider>
  )
}

export default App
