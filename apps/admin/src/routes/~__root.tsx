import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'
import type { RouterContext } from '@/router'
import { AdminSidebar } from '@/components/AdminSidebar'

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
})

function RootLayout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AdminSidebar />
      <div className="ml-64 min-h-screen flex flex-col">
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
