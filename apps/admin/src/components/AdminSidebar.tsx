import { Link, useRouter } from '@tanstack/react-router'
import { Building2, Users, BarChart3, ShieldCheck, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils'
import { clearAuth, getStoredUser } from '@/utils/auth'

const navigation = [
  { name: 'Organizations', to: '/organizations', icon: Building2 },
  { name: 'Users', to: '/users', icon: Users },
  { name: 'Analytics', to: '/analytics', icon: BarChart3 },
] as const

export function AdminSidebar() {
  const router = useRouter()
  const user = getStoredUser()

  function handleLogout() {
    clearAuth()
    void router.navigate({ to: '/' })
  }

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col bg-[#142236] border-r border-[#0e1724] text-white">
      <div className="flex h-16 flex-shrink-0 items-center justify-center border-b border-[#0e1724] gap-2">
        <ShieldCheck className="h-5 w-5 text-primary-400" />
        <h1 className="font-bold text-xl text-white">
          Majster<span className="text-primary-400">AI</span>
          <span className="ml-1.5 text-xs font-medium text-white/50 tracking-widest uppercase">Admin</span>
        </h1>
      </div>

      <nav className="flex-1 min-h-0 overflow-y-auto flex flex-col gap-1 p-4">
        {navigation.map((item) => (
          <Link
            key={item.name}
            to={item.to}
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors hover:bg-white/10',
            )}
            activeProps={{ className: 'bg-white/10 text-white border-l-2 border-l-primary-400' }}
            inactiveProps={{ className: 'text-white/80' }}
          >
            <item.icon className="h-5 w-5 flex-shrink-0" />
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>

      <div className="flex-shrink-0 border-t border-[#0e1724] p-4 space-y-2">
        {user && (
          <div className="px-3 py-1">
            <p className="text-xs text-white/40 truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-white/70 hover:bg-white/10 hover:text-white transition-colors"
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  )
}
