/** Platform admin – landing with links to Organizations and Users. */

import { NavLink, Outlet } from 'react-router-dom'
import { Building2, Users } from 'lucide-react'
import { cn } from '@/lib/utils'

const adminNav = [
  { name: 'Organizations', href: '/admin/organizations', icon: Building2 },
  { name: 'Users', href: '/admin/users', icon: Users },
]

export function AdminPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Platform Admin</h1>
        <p className="mt-2 text-sm text-slate-600">Manage organizations and users (superadmin only).</p>
      </div>
      <nav className="flex gap-2 mb-6 border-b border-slate-200">
        {adminNav.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 -mb-px',
                isActive
                  ? 'border-slate-900 text-slate-900 dark:border-slate-100 dark:text-slate-100'
                  : 'border-transparent text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.name}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}
