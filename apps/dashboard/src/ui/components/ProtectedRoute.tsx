import { Navigate, useLocation } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAppSelector((state) => state.auth.token)
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}
