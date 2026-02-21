/** Services – trade categories and services (Sophiie-style) with full CRUD. */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { apiClient } from '@/infrastructure/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

interface TradeCategory {
  id: number
  org_id: string
  name: string
  type: string | null
  created_at: number
  updated_at: number
}

interface TradeService {
  id: number
  org_id: string
  name: string
  description: string | null
  duration: number | null
  duration_unit: string | null
  pricing_mode: string | null
  fixed_price: number | null
  hourly_rate: number | null
  is_active: boolean
  trade_category_id: number | null
  created_at: number
  updated_at: number
}

export function ServicesPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const [categoryModalOpen, setCategoryModalOpen] = useState(false)
  const [categoryEditId, setCategoryEditId] = useState<number | null>(null)
  const [categoryName, setCategoryName] = useState('')
  const [categoryType, setCategoryType] = useState('')
  const [serviceModalOpen, setServiceModalOpen] = useState(false)
  const [serviceEditId, setServiceEditId] = useState<number | null>(null)
  const [serviceName, setServiceName] = useState('')
  const [serviceDescription, setServiceDescription] = useState('')
  const [serviceCategoryId, setServiceCategoryId] = useState<string>('')
  const [serviceIsActive, setServiceIsActive] = useState(true)

  const orgId = currentOrganization?.id ?? ''

  const { data: categories = [] } = useQuery({
    queryKey: ['trade-categories', orgId],
    queryFn: async () => {
      const { data } = await apiClient.get<TradeCategory[]>(
        `/api/trade-categories/org/${orgId}`
      )
      return data
    },
    enabled: !!orgId,
  })

  const { data: services = [] } = useQuery({
    queryKey: ['trade-services', orgId],
    queryFn: async () => {
      const { data } = await apiClient.get<TradeService[]>(
        `/api/trade-services/org/${orgId}`
      )
      return data
    },
    enabled: !!orgId,
  })

  const createCategory = useMutation({
    mutationFn: () =>
      apiClient.post<TradeCategory>('/api/trade-categories/', {
        org_id: orgId,
        name: categoryName,
        type: categoryType || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trade-categories', orgId] })
      setCategoryModalOpen(false)
      setCategoryName('')
      setCategoryType('')
      setCategoryEditId(null)
    },
  })

  const updateCategory = useMutation({
    mutationFn: (id: number) =>
      apiClient.put<TradeCategory>(`/api/trade-categories/${id}`, {
        name: categoryName,
        type: categoryType || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trade-categories', orgId] })
      setCategoryModalOpen(false)
      setCategoryEditId(null)
      setCategoryName('')
      setCategoryType('')
    },
  })

  const deleteCategory = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/trade-categories/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trade-categories', orgId] })
    },
  })

  const createService = useMutation({
    mutationFn: () =>
      apiClient.post<TradeService>('/api/trade-services/', {
        org_id: orgId,
        name: serviceName,
        description: serviceDescription || null,
        trade_category_id: serviceCategoryId ? parseInt(serviceCategoryId, 10) : null,
        is_active: serviceIsActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trade-services', orgId] })
      setServiceModalOpen(false)
      setServiceName('')
      setServiceDescription('')
      setServiceCategoryId('')
      setServiceIsActive(true)
      setServiceEditId(null)
    },
  })

  const updateService = useMutation({
    mutationFn: (id: number) =>
      apiClient.put<TradeService>(`/api/trade-services/${id}`, {
        name: serviceName,
        description: serviceDescription || null,
        trade_category_id: serviceCategoryId ? parseInt(serviceCategoryId, 10) : null,
        is_active: serviceIsActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trade-services', orgId] })
      setServiceModalOpen(false)
      setServiceEditId(null)
      setServiceName('')
      setServiceDescription('')
      setServiceCategoryId('')
      setServiceIsActive(true)
    },
  })

  const deleteService = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/trade-services/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trade-services', orgId] })
    },
  })

  const openEditCategory = (c: TradeCategory) => {
    setCategoryEditId(c.id)
    setCategoryName(c.name)
    setCategoryType(c.type ?? '')
    setCategoryModalOpen(true)
  }

  const openAddCategory = () => {
    setCategoryEditId(null)
    setCategoryName('')
    setCategoryType('')
    setCategoryModalOpen(true)
  }

  const openEditService = (s: TradeService) => {
    setServiceEditId(s.id)
    setServiceName(s.name)
    setServiceDescription(s.description ?? '')
    setServiceCategoryId(s.trade_category_id != null ? String(s.trade_category_id) : '')
    setServiceIsActive(s.is_active)
    setServiceModalOpen(true)
  }

  const openAddService = () => {
    setServiceEditId(null)
    setServiceName('')
    setServiceDescription('')
    setServiceCategoryId('')
    setServiceIsActive(true)
    setServiceModalOpen(true)
  }

  const handleCategorySubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (categoryEditId != null) {
      updateCategory.mutate(categoryEditId)
    } else {
      createCategory.mutate()
    }
  }

  const handleServiceSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (serviceEditId != null) {
      updateService.mutate(serviceEditId)
    } else {
      createService.mutate()
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Services</h1>
        <p className="mt-2 text-sm text-slate-600">
          Trade categories and services
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Categories</CardTitle>
            <Button variant="accent" onClick={openAddCategory}>
              Add category
            </Button>
          </CardHeader>
          <CardContent>
            {categories.length === 0 ? (
              <p className="text-sm text-slate-500">No categories yet.</p>
            ) : (
              <ul className="space-y-2">
                {categories.map((c) => (
                  <li
                    key={c.id}
                    className="flex items-center justify-between rounded border border-slate-100 py-2 px-3 text-sm"
                  >
                    <span className="font-medium">{c.name}</span>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" onClick={() => openEditCategory(c)}>
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600"
                        onClick={() => {
                          if (window.confirm('Delete this category?')) {
                            deleteCategory.mutate(c.id)
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Services</CardTitle>
            <Button variant="accent" onClick={openAddService}>
              Add service
            </Button>
          </CardHeader>
          <CardContent>
            {services.length === 0 ? (
              <p className="text-sm text-slate-500">No services yet.</p>
            ) : (
              <ul className="space-y-2">
                {services.map((s) => (
                  <li
                    key={s.id}
                    className="flex items-center justify-between rounded border border-slate-100 py-2 px-3 text-sm"
                  >
                    <div>
                      <span className="font-medium">{s.name}</span>
                      {!s.is_active && (
                        <span className="ml-2 text-xs text-slate-400">(inactive)</span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" onClick={() => openEditService(s)}>
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600"
                        onClick={() => {
                          if (window.confirm('Delete this service?')) {
                            deleteService.mutate(s.id)
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Modal
        open={categoryModalOpen}
        onClose={() => setCategoryModalOpen(false)}
        title={categoryEditId != null ? 'Edit category' : 'Add category'}
      >
        <form className="space-y-4" onSubmit={handleCategorySubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-700">Name</label>
            <Input
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
              placeholder="Category name"
              className="mt-1"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Type</label>
            <Input
              value={categoryType}
              onChange={(e) => setCategoryType(e.target.value)}
              placeholder="Optional type"
              className="mt-1"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setCategoryModalOpen(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="accent"
              disabled={createCategory.isPending || updateCategory.isPending}
            >
              {categoryEditId != null ? 'Save' : 'Add'}
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        open={serviceModalOpen}
        onClose={() => setServiceModalOpen(false)}
        title={serviceEditId != null ? 'Edit service' : 'Add service'}
      >
        <form className="space-y-4" onSubmit={handleServiceSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-700">Name</label>
            <Input
              value={serviceName}
              onChange={(e) => setServiceName(e.target.value)}
              placeholder="Service name"
              className="mt-1"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Description</label>
            <Input
              value={serviceDescription}
              onChange={(e) => setServiceDescription(e.target.value)}
              placeholder="Optional description"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Category</label>
            <select
              value={serviceCategoryId}
              onChange={(e) => setServiceCategoryId(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">None</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="service-active"
              checked={serviceIsActive}
              onChange={(e) => setServiceIsActive(e.target.checked)}
              className="rounded border-slate-300"
            />
            <label htmlFor="service-active" className="text-sm text-slate-700">
              Active
            </label>
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setServiceModalOpen(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="accent"
              disabled={createService.isPending || updateService.isPending}
            >
              {serviceEditId != null ? 'Save' : 'Add'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
