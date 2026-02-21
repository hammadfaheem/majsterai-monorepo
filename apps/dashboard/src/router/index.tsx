import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'
import { ProtectedRoute } from '@/ui/components/ProtectedRoute'
import { DashboardLayout } from '@/ui/layout/DashboardLayout'
import { LoginPage } from '@/ui/pages/LoginPage'
import { RegisterPage } from '@/ui/pages/RegisterPage'
import { TestAgentPage } from '@/ui/pages/TestAgentPage'
import { DashboardPage } from '@/ui/pages/DashboardPage'
import { LeadsPage } from '@/ui/pages/LeadsPage'
import { LeadDetailPage } from '@/ui/pages/LeadDetailPage'
import { CallHistoryPage } from '@/ui/pages/CallHistoryPage'
import { TeamPage } from '@/ui/pages/TeamPage'
import { SettingsPage } from '@/ui/pages/SettingsPage'
import { AppointmentsPage } from '@/ui/pages/AppointmentsPage'
import { ServicesPage } from '@/ui/pages/ServicesPage'
import { InvoicesPage } from '@/ui/pages/InvoicesPage'
import { AgentConfigPage } from '@/ui/pages/AgentConfigPage'
import { ScenariosPage } from '@/ui/pages/ScenariosPage'
import { TransfersPage } from '@/ui/pages/TransfersPage'
import { SchedulesPage } from '@/ui/pages/SchedulesPage'
import { DepartmentsPage } from '@/ui/pages/DepartmentsPage'
import { TagsPage } from '@/ui/pages/TagsPage'
import { TasksPage } from '@/ui/pages/TasksPage'
import { AdminGuard } from '@/ui/components/AdminGuard'
import { AdminPage } from '@/ui/pages/AdminPage'
import { AdminOrganizationsPage } from '@/ui/pages/AdminOrganizationsPage'
import { AdminUsersPage } from '@/ui/pages/AdminUsersPage'

export function Router() {
  const token = useAppSelector((state) => state.auth.token)

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          token ? (
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          ) : (
            <Navigate to="/login" replace />
          )
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="leads" element={<LeadsPage />} />
        <Route path="leads/:id" element={<LeadDetailPage />} />
        <Route path="calls" element={<CallHistoryPage />} />
        <Route path="team" element={<TeamPage />} />
        <Route path="appointments" element={<AppointmentsPage />} />
        <Route path="services" element={<ServicesPage />} />
        <Route path="invoices" element={<InvoicesPage />} />
        <Route path="agent" element={<AgentConfigPage />} />
        <Route path="scenarios" element={<ScenariosPage />} />
        <Route path="transfers" element={<TransfersPage />} />
        <Route path="schedules" element={<SchedulesPage />} />
        <Route path="departments" element={<DepartmentsPage />} />
        <Route path="tags" element={<TagsPage />} />
        <Route path="tasks" element={<TasksPage />} />
        <Route path="test-agent" element={<TestAgentPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="admin" element={<AdminGuard />}>
          <Route index element={<Navigate to="/admin/organizations" replace />} />
          <Route element={<AdminPage />}>
            <Route path="organizations" element={<AdminOrganizationsPage />} />
            <Route path="users" element={<AdminUsersPage />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  )
}
