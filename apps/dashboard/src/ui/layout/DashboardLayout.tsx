import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { TestAgentWidget } from '@/ui/test-agent/TestAgentWidget'
export function DashboardLayout() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div className="flex flex-col min-h-screen transition-all duration-300 ml-0 md:ml-64">
        <Header />

        <main className="flex-1 min-h-0 p-6">
          <Outlet />
        </main>
      </div>

      <TestAgentWidget />
    </div>
  )
}
