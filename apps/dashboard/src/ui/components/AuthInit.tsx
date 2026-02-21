import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { setUser } from '@/store/authSlice'
import { userService } from '@/application/user/userService'

/** Restores user from API when token exists but user is missing (e.g. after refresh). */
export function AuthInit({ children }: { children: React.ReactNode }) {
  const { token, user } = useAppSelector((state) => state.auth)
  const dispatch = useAppDispatch()

  useEffect(() => {
    if (!token || user) return
    userService
      .getCurrentUser()
      .then((u) => dispatch(setUser(u)))
      .catch(() => {
        // Token invalid; logout is handled by 401 interceptor if we hit a protected endpoint
      })
  }, [token, user, dispatch])

  return <>{children}</>
}
