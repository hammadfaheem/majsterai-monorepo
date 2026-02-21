import { Navigate, Outlet } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'

/** Renders children (or Outlet) only if current user is SUPERADMIN; otherwise redirects to dashboard. */
export function AdminGuard({ children }: { children?: React.ReactNode }) {
  const user = useAppSelector((state) => state.auth.user)
  if (user?.role !== 'SUPERADMIN') {
    return <Navigate to="/dashboard" replace />
  }
  return children ? <>{children}</> : <Outlet />
}
