/** Onboarding data persisted across steps (localStorage). */

const STORAGE_KEY = 'majsterai_onboarding'

export interface OnboardingData {
  org_name: string
  time_zone: string
  country: string
  currency: string
}

const defaults: OnboardingData = {
  org_name: '',
  time_zone: 'UTC',
  country: '',
  currency: 'USD',
}

export function getOnboardingData(): OnboardingData | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Partial<OnboardingData>
    return { ...defaults, ...parsed }
  } catch {
    return null
  }
}

export function setOnboardingData(data: Partial<OnboardingData>): void {
  const current = getOnboardingData() ?? defaults
  const merged = { ...current, ...data }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))
}

export function clearOnboardingData(): void {
  localStorage.removeItem(STORAGE_KEY)
}
