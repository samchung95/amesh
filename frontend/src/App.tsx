import { LoaderCircle, LogOut, RotateCcw } from 'lucide-react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { ApiError } from './api/client'
import type { Capability, UiSession } from './api/types'
import { useSession } from './app/queries'
import { useAppSettings } from './app/settings'
import { AppShell } from './components/AppShell'
import { ConnectionGate } from './components/ConnectionGate'
import { DashboardPage } from './pages/DashboardPage'
import { ExecutionDetailPage } from './pages/ExecutionDetailPage'
import { ExecutionsPage } from './pages/ExecutionsPage'
import { FlowDetailPage } from './pages/FlowDetailPage'
import { FlowEditorPage } from './pages/FlowEditorPage'
import { FlowsPage } from './pages/FlowsPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { NamespaceResourcesPage } from './pages/NamespaceResourcesPage'
import { PluginsPage } from './pages/PluginsPage'
import { SearchPage } from './pages/SearchPage'
import { TriggersPage } from './pages/TriggersPage'
import { ChecksPage } from './pages/ChecksPage'
import { AdministrationPage } from './pages/AdministrationPage'
import { BlueprintsPage } from './pages/BlueprintsPage'

export function App() {
  const { connected } = useAppSettings()
  return connected ? <AuthenticatedApp /> : <ConnectionGate />
}

function AuthenticatedApp() {
  const session = useSession()
  const { disconnect } = useAppSettings()

  if (session.isPending) {
    return (
      <main className="bootstrap-state" role="status" aria-live="polite">
        <LoaderCircle className="spin" size={28} aria-hidden="true" />
        <h1>Opening control room</h1>
        <p>Loading server-authoritative workspace permissions.</p>
      </main>
    )
  }
  if (session.error) {
    if (session.error instanceof ApiError && session.error.status === 401) {
      return <ConnectionGate onConnected={() => void session.refetch()} />
    }
    return (
      <main className="bootstrap-state bootstrap-error" role="alert">
        <h1>Connection refused</h1>
        <p>{session.error.message}</p>
        <div>
          <button className="button button-primary" type="button" onClick={() => void session.refetch()}><RotateCcw size={17} aria-hidden="true" />Try again</button>
          <button className="button button-secondary" type="button" onClick={disconnect}><LogOut size={17} aria-hidden="true" />Change connection</button>
        </div>
      </main>
    )
  }

  return <WorkspaceRoutes session={session.data} />
}

function CapabilityRoute({ session, capability, title, children }: { session: UiSession; capability: Capability; title: string; children: React.ReactNode }) {
  return session.capabilities[capability] ? children : <PlaceholderPage title={title} denied />
}

function WorkspaceRoutes({ session }: { session: UiSession }) {
  return (
    <Routes>
      <Route element={<AppShell session={session} />}>
        <Route index element={<CapabilityRoute session={session} capability="dashboards.view" title="Dashboard"><DashboardPage session={session} /></CapabilityRoute>} />
        <Route path="search" element={<CapabilityRoute session={session} capability="search.view" title="Search"><SearchPage session={session} /></CapabilityRoute>} />
        <Route path="flows" element={<CapabilityRoute session={session} capability="flows.view" title="Flows"><FlowsPage session={session} /></CapabilityRoute>} />
        <Route path="blueprints" element={<CapabilityRoute session={session} capability="flows.view" title="Blueprints"><BlueprintsPage session={session} /></CapabilityRoute>} />
        <Route path="flows/new" element={<CapabilityRoute session={session} capability="flows.create" title="Create flow"><FlowEditorPage session={session} /></CapabilityRoute>} />
        <Route path="flows/:namespace/:flowId/edit" element={<CapabilityRoute session={session} capability="flows.update" title="Edit flow"><FlowEditorPage session={session} /></CapabilityRoute>} />
        <Route path="flows/:namespace/:flowId" element={<CapabilityRoute session={session} capability="flows.view" title="Flow"><FlowDetailPage session={session} /></CapabilityRoute>} />
        <Route path="executions" element={<CapabilityRoute session={session} capability="executions.view" title="Executions"><ExecutionsPage session={session} /></CapabilityRoute>} />
        <Route path="executions/:executionId" element={<CapabilityRoute session={session} capability="executions.view" title="Execution"><ExecutionDetailPage session={session} /></CapabilityRoute>} />
        <Route path="triggers" element={<CapabilityRoute session={session} capability="triggers.view" title="Triggers"><TriggersPage session={session} /></CapabilityRoute>} />
        <Route path="checks" element={<CapabilityRoute session={session} capability="checks.view" title="Checks"><ChecksPage session={session} /></CapabilityRoute>} />
        <Route path="namespaces" element={<CapabilityRoute session={session} capability="namespaceResources.read" title="Namespaces"><NamespaceResourcesPage session={session} /></CapabilityRoute>} />
        <Route path="assets" element={<PlaceholderPage title="Assets" />} />
        <Route path="apps" element={<PlaceholderPage title="Apps" />} />
        <Route path="plugins" element={<CapabilityRoute session={session} capability="plugins.view" title="Plugins"><PluginsPage session={session} /></CapabilityRoute>} />
        <Route path="administration" element={<CapabilityRoute session={session} capability="administration.manage" title="Administration"><AdministrationPage session={session} /></CapabilityRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
