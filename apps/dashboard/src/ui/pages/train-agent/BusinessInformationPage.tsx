/** Business Information – configure company details, location, trading hours, and social profiles. */

import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { organizationService } from '@/application/organization/organizationService'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Check, MapPin, Clock, FileText, Layers, Share2 } from 'lucide-react'

const COMMON_TIMEZONES = [
  'UTC',
  'Europe/Warsaw',
  'Europe/London',
  'Europe/Berlin',
  'America/New_York',
  'America/Los_Angeles',
  'Asia/Tokyo',
  'Australia/Sydney',
]

const COUNTRIES = [
  { code: 'AU', name: 'Australia' },
  { code: 'US', name: 'United States' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'PL', name: 'Poland' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'CA', name: 'Canada' },
  { code: 'NZ', name: 'New Zealand' },
  { code: 'JP', name: 'Japan' },
]

const CURRENCIES = [
  { code: 'AUD', name: 'Australian Dollar (AUD)' },
  { code: 'USD', name: 'US Dollar (USD)' },
  { code: 'EUR', name: 'Euro (EUR)' },
  { code: 'GBP', name: 'British Pound (GBP)' },
  { code: 'PLN', name: 'Polish Złoty (PLN)' },
]

const BUSINESS_CATEGORIES = [
  'Hotel',
  'Restaurant',
  'Retail',
  'Healthcare',
  'Construction',
  'Cleaning',
  'Plumbing',
  'Electrical',
  'Landscaping',
  'Other',
]

const DAYS = [
  { id: 'mon', label: 'M' },
  { id: 'tue', label: 'T' },
  { id: 'wed', label: 'W' },
  { id: 'thu', label: 'T' },
  { id: 'fri', label: 'F' },
  { id: 'sat', label: 'S' },
  { id: 'sun', label: 'S' },
]

interface TradingSlot {
  days: string[]
  open: string
  close: string
}

interface BusinessInfo {
  public_email?: string
  business_phone?: string
  phone_country_code?: string
  website?: string
  location_type?: 'fixed' | 'mobile' | 'remote'
  business_description?: string
  main_category?: string
  service_types?: string[]
  year_founded?: number
  experience_years?: number
  social?: {
    instagram?: string
    x?: string
    facebook?: string
    linkedin?: string
  }
  trading_hours?: {
    time_zone: string
    slots: TradingSlot[]
  }
}

function getBusinessInfo(settings: Record<string, unknown> | null | undefined): BusinessInfo {
  const bi = settings?.business_info as Record<string, unknown> | undefined
  if (!bi) return {}
  return {
    public_email: bi.public_email as string | undefined,
    business_phone: bi.business_phone as string | undefined,
    phone_country_code: (bi.phone_country_code as string) ?? '+61',
    website: bi.website as string | undefined,
    location_type: bi.location_type as 'fixed' | 'mobile' | 'remote' | undefined,
    business_description: bi.business_description as string | undefined,
    main_category: bi.main_category as string | undefined,
    service_types: (bi.service_types as string[]) ?? [],
    year_founded: bi.year_founded as number | undefined,
    experience_years: bi.experience_years as number | undefined,
    social: bi.social as BusinessInfo['social'],
    trading_hours: bi.trading_hours as BusinessInfo['trading_hours'],
  }
}

export function BusinessInformationPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const orgId = currentOrganization?.id ?? ''
  const { data: orgData } = useQuery({
    queryKey: ['organization', orgId],
    queryFn: () => organizationService.getOrganization(orgId),
    enabled: !!orgId,
  })
  const org = (orgData ?? currentOrganization) as { settings?: Record<string, unknown> | null } | null

  const [companyName, setCompanyName] = useState('')
  const [publicEmail, setPublicEmail] = useState('')
  const [phoneCountryCode, setPhoneCountryCode] = useState('+61')
  const [businessPhone, setBusinessPhone] = useState('')
  const [website, setWebsite] = useState('')
  const [country, setCountry] = useState('')
  const [currency, setCurrency] = useState('AUD')
  const [locationType, setLocationType] = useState<'fixed' | 'mobile' | 'remote'>('fixed')
  const [timeZone, setTimeZone] = useState('Australia/Sydney')
  const [slots, setSlots] = useState<TradingSlot[]>([{ days: ['mon', 'tue', 'wed', 'thu', 'fri'], open: '09:00', close: '23:00' }])
  const [businessDescription, setBusinessDescription] = useState('')
  const [mainCategory, setMainCategory] = useState('')
  const [serviceTypes, setServiceTypes] = useState<string[]>([])
  const [yearFounded, setYearFounded] = useState<string>('')
  const [experienceYears, setExperienceYears] = useState<string>('')
  const [instagram, setInstagram] = useState('')
  const [xHandle, setXHandle] = useState('')
  const [facebook, setFacebook] = useState('')
  const [linkedin, setLinkedin] = useState('')

  const businessInfo = getBusinessInfo(org?.settings ?? null)

  useEffect(() => {
    if (currentOrganization) {
      const o = currentOrganization as { name?: string; country?: string | null; currency?: string; time_zone?: string }
      setCompanyName(o.name ?? '')
      setCountry(o.country ?? '')
      setCurrency(o.currency ?? 'USD')
      setTimeZone(o.time_zone ?? 'UTC')
    }
  }, [currentOrganization])

  useEffect(() => {
    setPublicEmail(businessInfo.public_email ?? '')
    setPhoneCountryCode(businessInfo.phone_country_code ?? '+61')
    setBusinessPhone(businessInfo.business_phone ?? '')
    setWebsite(businessInfo.website ?? '')
    setLocationType(businessInfo.location_type ?? 'fixed')
    setBusinessDescription(businessInfo.business_description ?? '')
    setMainCategory(businessInfo.main_category ?? '')
    setServiceTypes(businessInfo.service_types ?? [])
    setYearFounded(businessInfo.year_founded != null ? String(businessInfo.year_founded) : '')
    setExperienceYears(businessInfo.experience_years != null ? String(businessInfo.experience_years) : '')
    setInstagram(businessInfo.social?.instagram ?? '')
    setXHandle(businessInfo.social?.x ?? '')
    setFacebook(businessInfo.social?.facebook ?? '')
    setLinkedin(businessInfo.social?.linkedin ?? '')
    if (businessInfo.trading_hours) {
      setTimeZone(businessInfo.trading_hours.time_zone)
      if (businessInfo.trading_hours.slots?.length) setSlots(businessInfo.trading_hours.slots)
    }
  }, [org?.settings])

  const toggleServiceType = (t: string) => {
    setServiceTypes((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]))
  }

  const toggleSlotDay = (slotIndex: number, day: string) => {
    setSlots((prev) => {
      const next = [...prev]
      const slot = { ...next[slotIndex] }
      const days = slot.days.includes(day) ? slot.days.filter((d) => d !== day) : [...slot.days, day]
      slot.days = days
      next[slotIndex] = slot
      return next
    })
  }

  const addSlot = () => setSlots((prev) => [...prev, { days: [], open: '09:00', close: '17:00' }])
  const removeSlot = (i: number) => setSlots((prev) => prev.filter((_, idx) => idx !== i))
  const updateSlot = (i: number, field: 'open' | 'close', value: string) => {
    setSlots((prev) => {
      const next = [...prev]
      next[i] = { ...next[i], [field]: value }
      return next
    })
  }

  const updateOrg = useMutation({
    mutationFn: async () => {
      if (!currentOrganization) throw new Error('No organization')
      const settings = (org?.settings ?? {}) as Record<string, unknown>
      const business_info: BusinessInfo = {
        public_email: publicEmail || undefined,
        business_phone: businessPhone || undefined,
        phone_country_code: phoneCountryCode,
        website: website || undefined,
        location_type: locationType,
        business_description: businessDescription || undefined,
        main_category: mainCategory || undefined,
        service_types: serviceTypes.length ? serviceTypes : undefined,
        year_founded: yearFounded ? parseInt(yearFounded, 10) : undefined,
        experience_years: experienceYears ? parseInt(experienceYears, 10) : undefined,
        social:
          instagram || xHandle || facebook || linkedin
            ? { instagram: instagram || undefined, x: xHandle || undefined, facebook: facebook || undefined, linkedin: linkedin || undefined }
            : undefined,
        trading_hours: {
          time_zone: timeZone,
          slots,
        },
      }
      return organizationService.updateOrganization(currentOrganization.id, {
        name: companyName || undefined,
        country: country || undefined,
        currency: currency || undefined,
        time_zone: timeZone,
        settings: { ...settings, business_info },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      queryClient.invalidateQueries({ queryKey: ['organization', currentOrganization?.id] })
    },
  })

  if (!currentOrganization) {
    return (
      <div className="text-slate-600 dark:text-slate-400">
        Select an organization to configure business information.
      </div>
    )
  }

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 50 }, (_, i) => currentYear - i)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Business Information</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Configure your company details, location, trading hours, and social profiles for your voice AI agent.
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          updateOrg.mutate()
        }}
        className="space-y-6"
      >
        {/* Basic Information */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Check className="h-5 w-5 text-emerald-500" />
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Essential business details</p>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Company Name</label>
                <Input value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="Hammad Org" className="mt-1" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Public Email</label>
                <Input type="email" value={publicEmail} onChange={(e) => setPublicEmail(e.target.value)} placeholder="info@example.com" className="mt-1" />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Business Phone</label>
                <div className="mt-1 flex gap-2">
                  <Input value={phoneCountryCode} onChange={(e) => setPhoneCountryCode(e.target.value)} placeholder="+61" className="w-20" />
                  <Input value={businessPhone} onChange={(e) => setBusinessPhone(e.target.value)} placeholder="444444444" className="flex-1" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Website</label>
                <Input value={website} onChange={(e) => setWebsite(e.target.value)} placeholder="https://example.com" className="mt-1" />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Country</label>
                <select
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  className="mt-1 flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
                >
                  <option value="">Select country</option>
                  {COUNTRIES.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Currency</label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="mt-1 flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
                >
                  {CURRENCIES.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Location */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <MapPin className="h-5 w-5 text-slate-500" />
            <CardTitle>Location</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">Where you provide services</p>
            <div className="flex flex-wrap gap-4">
              {(['fixed', 'mobile', 'remote'] as const).map((t) => (
                <label key={t} className="flex cursor-pointer items-center gap-2">
                  <input
                    type="radio"
                    name="location"
                    checked={locationType === t}
                    onChange={() => setLocationType(t)}
                    className="h-4 w-4"
                  />
                  <span className="text-sm">
                    {t === 'fixed' && 'Fixed Location'}
                    {t === 'mobile' && 'Mobile Business'}
                    {t === 'remote' && 'Remote/Online Business'}
                  </span>
                </label>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Trading Hours */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Clock className="h-5 w-5 text-slate-500" />
            <CardTitle>Trading Hours</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Set availability</p>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Time zone</label>
              <select
                value={timeZone}
                onChange={(e) => setTimeZone(e.target.value)}
                className="mt-1 flex h-10 w-full max-w-xs rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
              >
                {COMMON_TIMEZONES.map((tz) => (
                  <option key={tz} value={tz}>
                    {tz}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-3">
              {slots.map((slot, i) => (
                <div key={i} className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 p-3 dark:border-slate-700">
                  <div className="flex gap-1">
                    {DAYS.map((d) => (
                      <button
                        key={d.id}
                        type="button"
                        onClick={() => toggleSlotDay(i, d.id)}
                        className={`flex h-8 w-8 items-center justify-center rounded text-xs font-medium ${
                          slot.days.includes(d.id)
                            ? 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900'
                            : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                        }`}
                      >
                        {d.label}
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-500">Open</span>
                    <Input type="time" value={slot.open} onChange={(e) => updateSlot(i, 'open', e.target.value)} className="w-28" />
                    <span className="text-sm text-slate-500">Close</span>
                    <Input type="time" value={slot.close} onChange={(e) => updateSlot(i, 'close', e.target.value)} className="w-28" />
                  </div>
                  {slots.length > 1 && (
                    <Button type="button" variant="ghost" size="sm" onClick={() => removeSlot(i)}>
                      Remove
                    </Button>
                  )}
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={addSlot}>
                Add time slot
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Business Description */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <FileText className="h-5 w-5 text-slate-500" />
            <CardTitle>Business Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">Detail your business offering</p>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Category</label>
              <select
                value={businessDescription || mainCategory}
                onChange={(e) => {
                  const v = e.target.value
                  setBusinessDescription(v)
                  if (!mainCategory) setMainCategory(v)
                }}
                className="mt-1 flex h-10 w-full max-w-xs rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
              >
                <option value="">Select category</option>
                {BUSINESS_CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Additional Details */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Layers className="h-5 w-5 text-slate-500" />
            <CardTitle>Additional Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Categorization and history</p>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Main Category</label>
              <select
                value={mainCategory}
                onChange={(e) => setMainCategory(e.target.value)}
                className="mt-1 flex h-10 w-full max-w-xs rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
              >
                <option value="">Select a category</option>
                {BUSINESS_CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Service Types</label>
              <div className="mt-2 flex flex-wrap gap-3">
                {['Domestic', 'Commercial', 'Industrial'].map((t) => (
                  <label key={t} className="flex cursor-pointer items-center gap-2">
                    <input
                      type="checkbox"
                      checked={serviceTypes.includes(t.toLowerCase())}
                      onChange={() => toggleServiceType(t.toLowerCase())}
                      className="h-4 w-4 rounded"
                    />
                    <span className="text-sm">{t}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Year Founded</label>
                <select
                  value={yearFounded}
                  onChange={(e) => setYearFounded(e.target.value)}
                  className="mt-1 flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
                >
                  <option value="">Select Year</option>
                  {years.map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Experience (Years)</label>
                <Input
                  type="number"
                  min={0}
                  value={experienceYears}
                  onChange={(e) => setExperienceYears(e.target.value)}
                  placeholder="0"
                  className="mt-1 max-w-[120px]"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Social Profiles */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Share2 className="h-5 w-5 text-slate-500" />
            <CardTitle>Social Profiles</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Connect your social media</p>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Instagram</label>
                <div className="mt-1 flex items-center gap-1">
                  <span className="text-slate-500">instagram.com/</span>
                  <Input value={instagram} onChange={(e) => setInstagram(e.target.value)} placeholder="username" className="flex-1" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">X.com</label>
                <div className="mt-1 flex items-center gap-1">
                  <span className="text-slate-500">x.com/</span>
                  <Input value={xHandle} onChange={(e) => setXHandle(e.target.value)} placeholder="username" className="flex-1" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Facebook</label>
                <div className="mt-1 flex items-center gap-1">
                  <span className="text-slate-500">facebook.com/</span>
                  <Input value={facebook} onChange={(e) => setFacebook(e.target.value)} placeholder="page-name" className="flex-1" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">LinkedIn</label>
                <div className="mt-1 flex items-center gap-1">
                  <span className="text-slate-500">linkedin.com/company/</span>
                  <Input value={linkedin} onChange={(e) => setLinkedin(e.target.value)} placeholder="company-name" className="flex-1" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" variant="accent" disabled={updateOrg.isPending}>
            {updateOrg.isPending ? 'Saving…' : 'Save changes'}
          </Button>
        </div>
      </form>
    </div>
  )
}
