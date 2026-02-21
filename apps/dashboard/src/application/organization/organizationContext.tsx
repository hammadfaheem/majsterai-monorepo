import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAppSelector } from '@/store/hooks'
import { organizationService } from './organizationService'
import type { Organization } from '@/domain/organization/types'

interface OrganizationContextType {
  currentOrganization: Organization | null
  setCurrentOrganization: (org: Organization | null) => void
  organizations: Organization[]
  isLoading: boolean
  error: Error | null
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(
  undefined
)

export function OrganizationProvider({ children }: { children: ReactNode }) {
  const token = useAppSelector((state) => state.auth.token)
  const [currentOrganization, setCurrentOrganization] =
    useState<Organization | null>(null)

  // Fetch organizations only when user is authenticated (avoids 401 and redirect loop)
  const {
    data: organizations = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['organizations', token],
    queryFn: () => organizationService.listOrganizations(),
    enabled: !!token,
  })

  // Set first organization as current if none selected
  useEffect(() => {
    if (organizations.length > 0 && !currentOrganization) {
      setCurrentOrganization(organizations[0])
    }
  }, [organizations, currentOrganization, setCurrentOrganization])

  return (
    <OrganizationContext.Provider
      value={{
        currentOrganization,
        setCurrentOrganization,
        organizations,
        isLoading,
        error: error as Error | null,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  )
}

export function useOrganization() {
  const context = useContext(OrganizationContext)
  if (context === undefined) {
    throw new Error(
      'useOrganization must be used within an OrganizationProvider'
    )
  }
  return context
}
