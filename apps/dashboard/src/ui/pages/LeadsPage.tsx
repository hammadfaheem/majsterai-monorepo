/** Leads page for managing leads. */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { leadService } from '@/application/lead/leadService'
import { DataTable } from '@/ui/components/DataTable'
import { FilterBar } from '@/ui/components/FilterBar'
import { StatusBadge } from '@/ui/components/StatusBadge'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'

export function LeadsPage() {
  const navigate = useNavigate()
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const [searchValue, setSearchValue] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [addModalOpen, setAddModalOpen] = useState(false)
  const [addName, setAddName] = useState('')
  const [addEmail, setAddEmail] = useState('')
  const [addPhone, setAddPhone] = useState('')
  const [addSource, setAddSource] = useState('')

  const { data: leads = [], isLoading, isError, error } = useQuery({
    queryKey: ['leads', currentOrganization?.id, statusFilter],
    queryFn: () =>
      leadService.listLeads(currentOrganization?.id || '', {
        status: statusFilter || undefined,
        limit: 100,
      }),
    enabled: !!currentOrganization?.id,
  })

  const createLead = useMutation({
    mutationFn: (data: { name: string; email?: string; phone?: string; source?: string }) =>
      leadService.createLead(currentOrganization!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads', currentOrganization?.id] })
      setAddModalOpen(false)
      setAddName('')
      setAddEmail('')
      setAddPhone('')
      setAddSource('')
    },
  })

  const filteredLeads = leads.filter((lead) => {
    if (!searchValue) return true
    const search = searchValue.toLowerCase()
    return (
      lead.name.toLowerCase().includes(search) ||
      lead.email?.toLowerCase().includes(search) ||
      lead.phone?.includes(search)
    )
  })

  const columns = [
    {
      key: 'name',
      header: 'Name',
    },
    {
      key: 'email',
      header: 'Email',
      render: (value: unknown) => (value ? String(value) : '-'),
    },
    {
      key: 'phone',
      header: 'Phone',
      render: (value: unknown) => (value ? String(value) : '-'),
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: unknown) => <StatusBadge status={String(value)} />,
    },
    {
      key: 'source',
      header: 'Source',
      render: (value: unknown) => (value ? String(value) : '-'),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 sm:text-3xl">Leads</h1>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Manage your customer leads
          </p>
        </div>
        <Button variant="accent" onClick={() => setAddModalOpen(true)}>
          Add Lead
        </Button>
      </div>

      <FilterBar
        searchValue={searchValue}
        onSearchChange={setSearchValue}
        searchPlaceholder="Search leads..."
        filterOptions={[
          {
            label: 'Status',
            value: statusFilter,
            options: [
              { value: 'new', label: 'New' },
              { value: 'contacted', label: 'Contacted' },
              { value: 'qualified', label: 'Qualified' },
              { value: 'converted', label: 'Converted' },
              { value: 'lost', label: 'Lost' },
            ],
            onChange: setStatusFilter,
          },
        ]}
      />

      <div className="rounded-lg border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800/30">
        {isLoading ? (
          <div className="py-12 text-center text-sm text-slate-500">
            Loading…
          </div>
        ) : isError ? (
          <div className="py-12 text-center">
            <p className="text-sm text-red-600">
              Failed to load leads. {error instanceof Error ? error.message : 'Please try again.'}
            </p>
          </div>
        ) : filteredLeads.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <p className="text-sm text-slate-500 text-center">
              {searchValue || statusFilter
                ? 'No leads match your filters.'
                : 'No leads yet – Add your first lead'}
            </p>
            {!searchValue && !statusFilter && (
              <Button
                variant="accent"
                className="mt-4"
                onClick={() => setAddModalOpen(true)}
              >
                Add Lead
              </Button>
            )}
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredLeads as unknown as Record<string, unknown>[]}
            onRowClick={(lead) => navigate(`/leads/${(lead as { id: string }).id}`)}
          />
        )}
      </div>

      <Modal open={addModalOpen} onClose={() => setAddModalOpen(false)} title="Add Lead">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            createLead.mutate({
              name: addName,
              email: addEmail || undefined,
              phone: addPhone || undefined,
              source: addSource || undefined,
            })
          }}
        >
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Name</label>
            <Input
              value={addName}
              onChange={(e) => setAddName(e.target.value)}
              placeholder="Lead name"
              className="mt-1"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Email</label>
            <Input
              type="email"
              value={addEmail}
              onChange={(e) => setAddEmail(e.target.value)}
              placeholder="email@example.com"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Phone</label>
            <Input
              value={addPhone}
              onChange={(e) => setAddPhone(e.target.value)}
              placeholder="+1 234 567 8900"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Source</label>
            <Input
              value={addSource}
              onChange={(e) => setAddSource(e.target.value)}
              placeholder="e.g. Website"
              className="mt-1"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setAddModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={createLead.isPending}>
              {createLead.isPending ? 'Adding…' : 'Add Lead'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
