import { LoaderCircle, LogOut, RotateCcw } from 'lucide-react'
import { lazy, Suspense, type ComponentType, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'

import { ApiError } from './api/client'
import type { Capability, UiSession } from './api/types'
import { useSession } from './app/queries'
import { useAppSettings } from './app/settings'
import { AppShell } from './app/AppShell'
import { ConnectionGate } from './app/ConnectionGate'
import { PlaceholderPage } from './app/PlaceholderPage'
import { ChunkLoadErrorBoundary, LoadingState } from './shared/ui'

const PRELOAD_RELOAD_FLAG = 'amesh.ui.preload-reload.v1'
let preloadReloadAttempted = false

function reloadPage() {
  window.location.reload()
}

function installPreloadErrorReload() {
  if (typeof window === 'undefined') return
  const target = window as Window & { __ameshPreloadErrorReloadInstalled?: boolean }
  if (target.__ameshPreloadErrorReloadInstalled) return
  target.__ameshPreloadErrorReloadInstalled = true
  window.addEventListener('vite:preloadError', (event) => {
    event.preventDefault()
    if (preloadReloadAttempted) return
    preloadReloadAttempted = true
    try {
      if (window.sessionStorage.getItem(PRELOAD_RELOAD_FLAG) === '1') return
      window.sessionStorage.setItem(PRELOAD_RELOAD_FLAG, '1')
    } catch {
      // Storage can be unavailable in hardened browser modes; still try one recovery reload.
    }
    reloadPage()
  })
}

installPreloadErrorReload()

type SessionPageProps = { session: UiSession }
type AppsPageProps = SessionPageProps & { embedded?: boolean }

function lazyPage<Props>(loader: () => Promise<unknown>, exportName: string) {
  return lazy(async () => {
    const module = await loader() as Record<string, ComponentType<Props>>
    return { default: module[exportName] }
  })
}

const AdministrationPage = lazyPage<SessionPageProps>(() => import('./features/administration'), 'AdministrationPage')
const AgentSessionsPage = lazyPage<SessionPageProps>(() => import('./features/agent-sessions'), 'AgentSessionsPage')
const AgentsPage = lazyPage<SessionPageProps>(() => import('./features/agents'), 'AgentsPage')
const AppsPage = lazyPage<AppsPageProps>(() => import('./features/apps'), 'AppsPage')
const AssetsPage = lazyPage<SessionPageProps>(() => import('./features/assets'), 'AssetsPage')
const BlueprintsPage = lazyPage<SessionPageProps>(() => import('./features/blueprints'), 'BlueprintsPage')
const ChecksPage = lazyPage<SessionPageProps>(() => import('./features/checks'), 'ChecksPage')
const DashboardPage = lazyPage<SessionPageProps>(() => import('./features/dashboards'), 'DashboardPage')
const ExecutionDetailPage = lazyPage<SessionPageProps>(() => import('./features/executions'), 'ExecutionDetailPage')
const ExecutionsPage = lazyPage<SessionPageProps>(() => import('./features/executions'), 'ExecutionsPage')
const NamespaceResourcesPage = lazyPage<SessionPageProps>(() => import('./features/namespaces'), 'NamespaceResourcesPage')
const PluginsPage = lazyPage<SessionPageProps>(() => import('./features/plugins'), 'PluginsPage')
const ReleaseControlsPage = lazyPage<SessionPageProps>(() => import('./features/releases'), 'ReleaseControlsPage')
const SearchPage = lazyPage<SessionPageProps>(() => import('./features/search/SearchPage'), 'SearchPage')
const SessionOrchestratorPage = lazyPage<SessionPageProps>(() => import('./features/session-administration'), 'SessionOrchestratorPage')
const TriggersPage = lazyPage<SessionPageProps>(() => import('./features/triggers'), 'TriggersPage')
const FlowDetailPage = lazyPage<SessionPageProps>(() => import('./features/workflows/FlowDetailPage'), 'FlowDetailPage')
const FlowEditorPage = lazyPage<SessionPageProps>(() => import('./features/workflows/FlowEditorPage'), 'FlowEditorPage')
const FlowsPage = lazyPage<SessionPageProps>(() => import('./features/workflows/FlowsPage'), 'FlowsPage')
const FlowTestsPage = lazyPage<SessionPageProps>(() => import('./features/workflows/FlowTestsPage'), 'FlowTestsPage')

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

  return <WorkspaceRoutes session={{ ...session.data, namespace: session.data.namespace ?? null }} />
}

export function RouteSuspense({ title, children }: { title: string; children: ReactNode }) {
  const { t } = useTranslation()
  const location = useLocation()
  return (
    <ChunkLoadErrorBoundary resetKey={location.pathname} message={t('routeLoadError')} actionLabel={t('reload')} onReload={reloadPage}>
      <Suspense fallback={<LoadingState label={t('loadingRoute', { title })} />}>
        {children}
      </Suspense>
    </ChunkLoadErrorBoundary>
  )
}

function CapabilityRoute({ session, capability, title, children }: { session: UiSession; capability: Capability; title: string; children: ReactNode }) {
  return session.capabilities[capability] ? <RouteSuspense title={title}>{children}</RouteSuspense> : <PlaceholderPage title={title} denied />
}

function WorkspaceRoutes({ session }: { session: UiSession }) {
  return (
    <Routes>
      <Route path="embed/apps/:namespace/:appId" element={<CapabilityRoute session={session} capability="apps.view" title="App"><AppsPage session={session} embedded /></CapabilityRoute>} />
      <Route element={<AppShell session={session} />}>
        <Route index element={<CapabilityRoute session={session} capability="dashboards.view" title="Dashboard"><DashboardPage session={session} /></CapabilityRoute>} />
        <Route path="search" element={<CapabilityRoute session={session} capability="search.view" title="Search"><SearchPage session={session} /></CapabilityRoute>} />
        <Route path="flows" element={<CapabilityRoute session={session} capability="flows.view" title="Flows"><FlowsPage session={session} /></CapabilityRoute>} />
        <Route path="blueprints" element={<CapabilityRoute session={session} capability="flows.view" title="Blueprints"><BlueprintsPage session={session} /></CapabilityRoute>} />
        <Route path="flows/new" element={<CapabilityRoute session={session} capability="flows.create" title="Create workflow"><FlowEditorPage session={session} /></CapabilityRoute>} />
        <Route path="flows/:namespace/:flowId/edit" element={<CapabilityRoute session={session} capability="flows.update" title="Edit flow"><FlowEditorPage session={session} /></CapabilityRoute>} />
        <Route path="flows/:namespace/:flowId/tests" element={<CapabilityRoute session={session} capability="flowTests.view" title="Flow tests"><FlowTestsPage session={session} /></CapabilityRoute>} />
        <Route path="flows/:namespace/:flowId" element={<CapabilityRoute session={session} capability="flows.view" title="Flow"><FlowDetailPage session={session} /></CapabilityRoute>} />
        <Route path="executions" element={<CapabilityRoute session={session} capability="executions.view" title="Executions"><ExecutionsPage session={session} /></CapabilityRoute>} />
        <Route path="executions/:executionId" element={<CapabilityRoute session={session} capability="executions.view" title="Execution"><ExecutionDetailPage session={session} /></CapabilityRoute>} />
        <Route path="triggers" element={<CapabilityRoute session={session} capability="triggers.view" title="Triggers"><TriggersPage session={session} /></CapabilityRoute>} />
        <Route path="checks" element={<CapabilityRoute session={session} capability="checks.view" title="Checks"><ChecksPage session={session} /></CapabilityRoute>} />
        <Route path="namespaces" element={<CapabilityRoute session={session} capability="namespaceResources.read" title="Namespaces"><NamespaceResourcesPage session={session} /></CapabilityRoute>} />
        <Route path="assets" element={<CapabilityRoute session={session} capability="assets.view" title="Assets"><AssetsPage session={session} /></CapabilityRoute>} />
        <Route path="agents" element={<CapabilityRoute session={session} capability="agents.view" title="Agents"><AgentsPage session={session} /></CapabilityRoute>} />
        <Route path="agent-sessions" element={<CapabilityRoute session={session} capability="agentSessions.view" title="Agent sessions"><AgentSessionsPage session={session} /></CapabilityRoute>} />
        <Route path="session-administration" element={<CapabilityRoute session={session} capability="agentSessionAdministration.view" title="Session orchestrator"><SessionOrchestratorPage session={session} /></CapabilityRoute>} />
        <Route path="apps" element={<CapabilityRoute session={session} capability="apps.view" title="Apps"><AppsPage session={session} /></CapabilityRoute>} />
        <Route path="apps/:namespace/:appId" element={<CapabilityRoute session={session} capability="apps.view" title="App"><AppsPage session={session} /></CapabilityRoute>} />
        <Route path="plugins" element={<CapabilityRoute session={session} capability="plugins.view" title="Plugins"><PluginsPage session={session} /></CapabilityRoute>} />
        <Route path="releases" element={<CapabilityRoute session={session} capability="releases.view" title="Releases"><ReleaseControlsPage session={session} /></CapabilityRoute>} />
        <Route path="administration" element={<CapabilityRoute session={session} capability="administration.manage" title="Administration"><AdministrationPage session={session} /></CapabilityRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
