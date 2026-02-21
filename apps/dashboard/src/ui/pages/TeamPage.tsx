/** Team page for managing organization members and time off. */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { membershipService } from '@/application/membership/membershipService'
import { membershipUnavailabilityService } from '@/application/membership_unavailability/membershipUnavailabilityService'
import { DataTable } from '@/ui/components/DataTable'
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { Input } from '@/ui/components/Input'
import { Modal } from '@/ui/components/Modal'
import { Select } from '@/ui/components/Select'
import type { Membership } from '@/domain/membership/types'

const ROLE_OPTIONS = [
  { value: 'member', label: 'Member' },
  { value: 'admin', label: 'Admin' },
  { value: 'owner', label: 'Owner' },
]

export function TeamPage() {
  const { currentOrganization } = useOrganization()
  const queryClient = useQueryClient()
  const [addModalOpen, setAddModalOpen] = useState(false)
  const [addUserId, setAddUserId] = useState('')
  const [addRole, setAddRole] = useState('member')
  const [addInvitedEmail, setAddInvitedEmail] = useState('')
  const [addSchedulingPriority, setAddSchedulingPriority] = useState<string>('')
  const [addResponsibility, setAddResponsibility] = useState('')
  const [addPersonalisationNotes, setAddPersonalisationNotes] = useState('')
  const [addIsPointOfEscalation, setAddIsPointOfEscalation] = useState(false)
  const [timeOffModalOpen, setTimeOffModalOpen] = useState(false)
  const [timeOffMemberId, setTimeOffMemberId] = useState('')
  const [timeOffStartDate, setTimeOffStartDate] = useState('')
  const [timeOffEndDate, setTimeOffEndDate] = useState('')

  const { data: members = [], isLoading } = useQuery({
    queryKey: ['members', currentOrganization?.id],
    queryFn: () => membershipService.listMembers(currentOrganization?.id || ''),
    enabled: !!currentOrganization?.id,
  })

  const addMember = useMutation({
    mutationFn: (data: {
      user_id: string
      role?: string
      invited_email?: string
      scheduling_priority?: number
      responsibility?: string
      personalisation_notes?: string
      is_point_of_escalation?: boolean
    }) => membershipService.addMember(currentOrganization!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members', currentOrganization?.id] })
      setAddModalOpen(false)
      setAddUserId('')
      setAddRole('member')
      setAddInvitedEmail('')
      setAddSchedulingPriority('')
      setAddResponsibility('')
      setAddPersonalisationNotes('')
      setAddIsPointOfEscalation(false)
    },
  })

  const removeMember = useMutation({
    mutationFn: (userId: string) =>
      membershipService.removeMember(currentOrganization!.id, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members', currentOrganization?.id] })
    },
  })

  const { data: unavailabilities = [] } = useQuery({
    queryKey: ['membership-unavailability', currentOrganization?.id],
    queryFn: () => membershipUnavailabilityService.listByOrg(currentOrganization?.id ?? ''),
    enabled: !!currentOrganization?.id,
  })

  const addTimeOff = useMutation({
    mutationFn: () =>
      membershipUnavailabilityService.create({
        member_id: timeOffMemberId,
        start_date: timeOffStartDate ? new Date(timeOffStartDate).getTime() : null,
        end_date: timeOffEndDate ? new Date(timeOffEndDate).getTime() : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['membership-unavailability', currentOrganization?.id],
      })
      setTimeOffModalOpen(false)
      setTimeOffMemberId('')
      setTimeOffStartDate('')
      setTimeOffEndDate('')
    },
  })

  const deleteTimeOff = useMutation({
    mutationFn: (id: string) => membershipUnavailabilityService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['membership-unavailability', currentOrganization?.id],
      })
    },
  })

  const memberIdToLabel = (memberId: string) => {
    const m = members.find((x) => x.id === memberId)
    return m ? `User ${m.user_id.slice(0, 8)}…` : memberId.slice(0, 8)
  }

  const columns = [
    {
      key: 'user_id',
      header: 'User ID',
    },
    {
      key: 'role',
      header: 'Role',
      render: (value: unknown) => (
        <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
          {String(value)}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Joined',
      render: (value: unknown) => {
        if (!value) return '-'
        return new Date(Number(value)).toLocaleDateString()
      },
    },
    {
      key: '_actions',
      header: '',
      render: (_: unknown, row: Record<string, unknown>) => (
        <Button
          variant="ghost"
          size="sm"
          className="text-red-600 hover:text-red-700 hover:bg-red-50"
          onClick={(e) => {
            e.stopPropagation()
            if (window.confirm('Remove this member?')) {
              removeMember.mutate((row as unknown as Membership).user_id)
            }
          }}
          disabled={removeMember.isPending}
        >
          Remove
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 sm:text-3xl">Team</h1>
          <p className="mt-2 text-sm text-slate-600">
            Manage organization members
          </p>
        </div>
        <Button variant="accent" onClick={() => setAddModalOpen(true)}>
          Add Member
        </Button>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800/30">
        {isLoading ? (
          <div className="py-12 text-center text-sm text-slate-500">
            Loading...
          </div>
        ) : members.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <p className="text-sm text-slate-500 text-center">
              No members yet – Add your first team member
            </p>
            <Button
              variant="accent"
              className="mt-4"
              onClick={() => setAddModalOpen(true)}
            >
              Add Member
            </Button>
          </div>
        ) : (
          <DataTable columns={columns} data={members as unknown as Record<string, unknown>[]} />
        )}
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Time off</CardTitle>
          <Button
            variant="outline"
            onClick={() => setTimeOffModalOpen(true)}
            disabled={members.length === 0}
          >
            Add time off
          </Button>
        </CardHeader>
        <CardContent>
          {unavailabilities.length === 0 ? (
            <p className="text-sm text-slate-500">No time off entries.</p>
          ) : (
            <ul className="space-y-2">
              {unavailabilities.map((u) => (
                <li key={u.id} className="flex items-center justify-between text-sm">
                  <span>
                    {memberIdToLabel(u.member_id)} –{' '}
                    {u.start_date
                      ? new Date(u.start_date).toLocaleDateString()
                      : '—'}{' '}
                    to{' '}
                    {u.end_date
                      ? new Date(u.end_date).toLocaleDateString()
                      : '—'}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-600"
                    onClick={() => {
                      if (window.confirm('Remove this time off?')) {
                        deleteTimeOff.mutate(u.id)
                      }
                    }}
                  >
                    Remove
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Modal open={timeOffModalOpen} onClose={() => setTimeOffModalOpen(false)} title="Add time off">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            addTimeOff.mutate()
          }}
        >
          <div>
            <label className="block text-sm font-medium text-slate-700">Member</label>
            <select
              value={timeOffMemberId}
              onChange={(e) => setTimeOffMemberId(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              required
            >
              <option value="">Select member</option>
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  User {m.user_id.slice(0, 8)}…
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Start date</label>
            <Input
              type="date"
              value={timeOffStartDate}
              onChange={(e) => setTimeOffStartDate(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">End date</label>
            <Input
              type="date"
              value={timeOffEndDate}
              onChange={(e) => setTimeOffEndDate(e.target.value)}
              className="mt-1"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setTimeOffModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={addTimeOff.isPending}>
              Add
            </Button>
          </div>
        </form>
      </Modal>

      <Modal open={addModalOpen} onClose={() => setAddModalOpen(false)} title="Add Member">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            addMember.mutate({
              user_id: addUserId,
              role: addRole,
              invited_email: addInvitedEmail || undefined,
              scheduling_priority: addSchedulingPriority ? parseInt(addSchedulingPriority, 10) : undefined,
              responsibility: addResponsibility || undefined,
              personalisation_notes: addPersonalisationNotes || undefined,
              is_point_of_escalation: addIsPointOfEscalation,
            })
          }}
        >
          <div>
            <label className="block text-sm font-medium text-slate-700">User ID</label>
            <Input
              value={addUserId}
              onChange={(e) => setAddUserId(e.target.value)}
              placeholder="User ID (e.g. UUID)"
              className="mt-1"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Invited email</label>
            <Input
              type="email"
              value={addInvitedEmail}
              onChange={(e) => setAddInvitedEmail(e.target.value)}
              placeholder="Optional – for pending invites"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Role</label>
            <Select
              value={addRole}
              onChange={(e) => setAddRole(e.target.value)}
              className="mt-1"
            >
              {ROLE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Scheduling priority</label>
            <Input
              type="number"
              value={addSchedulingPriority}
              onChange={(e) => setAddSchedulingPriority(e.target.value)}
              placeholder="Optional number"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Responsibility</label>
            <Input
              value={addResponsibility}
              onChange={(e) => setAddResponsibility(e.target.value)}
              placeholder="e.g. Plumbing lead"
              className="mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Personalisation notes</label>
            <Input
              value={addPersonalisationNotes}
              onChange={(e) => setAddPersonalisationNotes(e.target.value)}
              placeholder="Optional notes"
              className="mt-1"
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="point-of-escalation"
              checked={addIsPointOfEscalation}
              onChange={(e) => setAddIsPointOfEscalation(e.target.checked)}
              className="h-4 w-4 rounded border-slate-300"
            />
            <label htmlFor="point-of-escalation" className="text-sm font-medium text-slate-700">
              Point of escalation
            </label>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setAddModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="accent" disabled={addMember.isPending}>
              {addMember.isPending ? 'Adding…' : 'Add Member'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
