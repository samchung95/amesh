import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Activity,
  AlertTriangle,
  Boxes,
  Database,
  FileKey,
  FolderTree,
  KeyRound,
  Network,
  RefreshCw,
  ScrollText,
  Settings2,
  ShieldCheck,
  UserRoundCog,
  Wrench,
} from 'lucide-react'
import { type FormEvent, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import type {
  AdministrationControl,
  AdministrationControlDraft,
  AdministrationImpactPreview,
  Announcement,
  AnnouncementAudience,
  AnnouncementSeverity,
  LifecycleJob,
  LifecycleLegalHold,
  LifecyclePolicy,
  LifecycleResourceType,
  LifecycleScope,
  OperationalBoundary,
  OperationalControl,
  OperationalControlScope,
  PrincipalDefinition,
  RoleBinding,
  UiSession,
} from '../api/types'
import { formatDate, formatNumber } from '../app/format'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'
import {
  administrationControlDraft,
  configurationValue,
  CONTROL_COPY,
  namespaceHierarchy,
  visibleConfiguration,
} from '../components/administrationModel'
import { StatusBadge } from '../components/StatusBadge'

type AdministrationView = 'namespaces' | 'access' | 'operations' | 'lifecycle' | 'controls' | 'configuration' | 'audit'

const views: Array<{ id: AdministrationView; label: string; icon: typeof FolderTree }> = [
  { id: 'namespaces', label: 'Namespaces', icon: FolderTree },
  { id: 'access', label: 'Access', icon: UserRoundCog },
  { id: 'operations', label: 'Operations', icon: Activity },
  { id: 'lifecycle', label: 'Lifecycle', icon: Database },
  { id: 'controls', label: 'Controls', icon: Wrench },
  { id: 'configuration', label: 'Configuration', icon: Settings2 },
  { id: 'audit', label: 'Audit', icon: ScrollText },
]

function expiryIn(days: number) {
  const value = new Date()
  value.setUTCDate(value.getUTCDate() + days)
  return value.toISOString()
}

function hoursFromNow(hours: number) {
  return new Date(Date.now() + hours * 60 * 60 * 1000).toISOString()
}

function fieldText(value: unknown, fallback: string): string {
  return typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'
    ? String(value)
    : fallback
}

export function AdministrationPage({ session }: { session: UiSession }) {
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const [params, setParams] = useSearchParams()
  const view = (params.get('view') as AdministrationView) || 'namespaces'
  const [notice, setNotice] = useState('')
  const [failure, setFailure] = useState('')

  const flows = useQuery({ queryKey: ['admin', 'flows', settings.tenant], queryFn: api.flows, enabled: view === 'namespaces' })
  const namespaceMetadata = useQuery({ queryKey: ['admin', 'namespace-metadata', settings.tenant, settings.namespace], queryFn: () => api.namespaceWorkflowMetadata(settings.namespace), enabled: view === 'namespaces' && Boolean(settings.namespace) })
  const namespaceFiles = useQuery({ queryKey: ['admin', 'namespace-files', settings.tenant, settings.namespace], queryFn: () => api.namespaceFiles(settings.namespace), enabled: view === 'namespaces' && Boolean(settings.namespace) })
  const namespaceKeys = useQuery({ queryKey: ['admin', 'namespace-keys', settings.tenant, settings.namespace], queryFn: () => api.namespaceKeyValues(settings.namespace), enabled: view === 'namespaces' && Boolean(settings.namespace) })
  const namespaceSecrets = useQuery({ queryKey: ['admin', 'namespace-secrets', settings.tenant, settings.namespace], queryFn: () => api.namespaceSecretBindings(settings.namespace), enabled: view === 'namespaces' && Boolean(settings.namespace) })

  const principals = useQuery({ queryKey: ['admin', 'principals'], queryFn: api.principals, enabled: view === 'access' })
  const roles = useQuery({ queryKey: ['admin', 'roles'], queryFn: api.roles, enabled: view === 'access' })
  const bindings = useQuery({ queryKey: ['admin', 'bindings'], queryFn: api.bindings, enabled: view === 'access' })
  const providers = useQuery({ queryKey: ['admin', 'providers'], queryFn: api.providers, enabled: view === 'access' })

  const readiness = useQuery({ queryKey: ['admin', 'readiness'], queryFn: api.readiness, enabled: view === 'operations', refetchInterval: 10_000 })
  const topology = useQuery({ queryKey: ['admin', 'topology'], queryFn: api.topology, enabled: view === 'operations', refetchInterval: 10_000 })
  const workers = useQuery({ queryKey: ['admin', 'workers'], queryFn: api.workers, enabled: view === 'operations', refetchInterval: 10_000 })
  const admission = useQuery({ queryKey: ['admin', 'admission'], queryFn: api.admissionDiagnostics, enabled: view === 'operations', refetchInterval: 10_000 })
  const search = useQuery({ queryKey: ['admin', 'search'], queryFn: api.searchStatus, enabled: view === 'operations', refetchInterval: 10_000 })

  const lifecyclePolicies = useQuery({ queryKey: ['admin', 'lifecycle', 'policies', settings.tenant], queryFn: api.lifecyclePolicies, enabled: view === 'lifecycle' })
  const lifecycleHolds = useQuery({ queryKey: ['admin', 'lifecycle', 'holds', settings.tenant], queryFn: api.lifecycleLegalHolds, enabled: view === 'lifecycle' })
  const lifecycleJobs = useQuery({ queryKey: ['admin', 'lifecycle', 'jobs', settings.tenant], queryFn: api.lifecycleJobs, enabled: view === 'lifecycle', refetchInterval: 10_000 })

  const controls = useQuery({ queryKey: ['admin', 'controls'], queryFn: api.administrationControls, enabled: view === 'controls' })
  const flags = useQuery({ queryKey: ['admin', 'flags', settings.tenant, settings.namespace], queryFn: api.featureFlags, enabled: view === 'controls' })
  const announcements = useQuery({ queryKey: ['admin', 'announcements', settings.tenant, settings.namespace], queryFn: () => api.announcements(settings.namespace || undefined, true), enabled: view === 'controls' })
  const operationalControls = useQuery({ queryKey: ['admin', 'operational-controls', settings.tenant], queryFn: api.operationalControls, enabled: view === 'controls' })
  const configuration = useQuery({ queryKey: ['admin', 'configuration'], queryFn: api.configuration, enabled: view === 'configuration' })
  const controlAudit = useQuery({ queryKey: ['admin', 'audit'], queryFn: api.administrationAudit, enabled: view === 'audit', refetchInterval: 10_000 })
  const indexedAudit = useQuery({ queryKey: ['admin', 'indexed-audit'], queryFn: () => api.search({ types: ['AUDIT'], limit: 100, sort: 'OCCURRED_AT', direction: 'DESC' }), enabled: view === 'audit' })

  const action = useMutation({
    mutationFn: async (operation: () => Promise<unknown>) => operation(),
    onSuccess: async () => {
      setFailure('')
      await queryClient.invalidateQueries({ queryKey: ['admin'] })
    },
    onError: (error) => setFailure(error.message),
  })

  const selected = views.find((item) => item.id === view) || views[0]
  const SelectedIcon = selected.icon
  return (
    <div className="page-stack administration-page">
      <header className="page-heading resource-heading">
        <div><p className="eyebrow">GOVERN / CONTROL PLANE</p><h1>Administration</h1><p>Tenant resources, identities, runtime posture and guarded operational controls.</p></div>
        <span className="admin-boundary"><ShieldCheck size={16} aria-hidden="true" />{session.display} · {settings.tenant}</span>
      </header>
      <nav className="admin-tabs" aria-label="Administration sections">
        {views.map(({ id, label, icon: Icon }) => <button type="button" className={view === id ? 'active' : ''} aria-current={view === id ? 'page' : undefined} key={id} onClick={() => setParams({ view: id })}><Icon size={16} aria-hidden="true" />{label}</button>)}
      </nav>
      <div className="admin-view-heading"><SelectedIcon size={20} aria-hidden="true" /><div><h2>{selected.label}</h2><p>Server-authoritative data and permissions for the selected tenant boundary.</p></div></div>
      {notice ? <p className="inline-notice" role="status">{notice}</p> : null}
      {failure ? <p className="form-error" role="alert">{failure}</p> : null}
      {view === 'namespaces' ? <NamespaceAdministration flows={flows.data || []} metadata={namespaceMetadata.data} files={namespaceFiles.data?.length || 0} keys={namespaceKeys.data?.length || 0} secrets={namespaceSecrets.data?.length || 0} namespace={settings.namespace} pending={flows.isPending} error={flows.error?.message} /> : null}
      {view === 'access' ? <AccessAdministration api={api} tenant={settings.tenant} principals={principals.data || []} roles={roles.data || []} bindings={bindings.data || []} providers={providers.data || []} pending={principals.isPending || roles.isPending || bindings.isPending || providers.isPending} mutate={(operation, message) => action.mutate(async () => { const result = await operation(); setNotice(message); return result })} /> : null}
      {view === 'operations' ? <OperationsAdministration readiness={readiness.data} topology={topology.data} workers={workers.data || []} admission={admission.data} search={search.data} pending={readiness.isPending || topology.isPending || admission.isPending || search.isPending} /> : null}
      {view === 'lifecycle' ? <LifecycleAdministration api={api} tenant={settings.tenant} namespace={settings.namespace} policies={lifecyclePolicies.data || []} holds={lifecycleHolds.data || []} jobs={lifecycleJobs.data || []} pending={lifecyclePolicies.isPending || lifecycleHolds.isPending || lifecycleJobs.isPending} onChanged={async (message) => { setNotice(message); setFailure(''); await queryClient.invalidateQueries({ queryKey: ['admin', 'lifecycle'] }) }} onFailure={setFailure} /> : null}
      {view === 'controls' ? <ControlsAdministration controls={controls.data || []} flags={flags.data || []} announcements={announcements.data || []} operationalControls={operationalControls.data || []} api={api} tenant={settings.tenant} namespace={settings.namespace} pending={controls.isPending || flags.isPending || announcements.isPending || operationalControls.isPending} onChanged={async (message) => { setNotice(message); setFailure(''); await queryClient.invalidateQueries({ queryKey: ['admin'] }) }} onFailure={setFailure} /> : null}
      {view === 'configuration' ? <ConfigurationAdministration snapshot={configuration.data} pending={configuration.isPending} onReload={() => action.mutate(async () => { const result = await api.reloadConfiguration(); setNotice(`Configuration reloaded at version ${String(result.version)}`); return result })} /> : null}
      {view === 'audit' ? <AuditAdministration direct={controlAudit.data || []} indexed={indexedAudit.data?.items || []} pending={controlAudit.isPending || indexedAudit.isPending} settings={settings} /> : null}
    </div>
  )
}

function NamespaceAdministration({ flows, metadata, files, keys, secrets, namespace, pending, error }: { flows: Array<{ namespace: string }>; metadata?: Awaited<ReturnType<ReturnType<typeof useApiClient>['namespaceWorkflowMetadata']>>; files: number; keys: number; secrets: number; namespace: string; pending: boolean; error?: string }) {
  const hierarchy = namespaceHierarchy([...flows.map((item) => item.namespace), namespace])
  if (pending) return <LoadingState label="Loading namespace hierarchy" />
  if (error) return <ErrorState message={error} retry={() => window.location.reload()} />
  return <div className="admin-split">
    <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">HIERARCHY</p><h3>Namespace tree</h3></div><span>{hierarchy.length} scopes</span></div>{hierarchy.length ? <ul className="namespace-tree">{hierarchy.map((item) => <li className={item.namespace === namespace ? 'selected' : ''} style={{ paddingLeft: `${String(14 + item.depth * 22)}px` }} key={item.namespace}><span>{item.direct ? '●' : '○'}</span><strong>{item.namespace}</strong>{item.namespace === namespace ? <em>selected</em> : null}</li>)}</ul> : <EmptyState title="No namespaces" body="Create or select a namespace to inspect inherited resources." />}</section>
    <div className="admin-panel-stack">
      <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">EFFECTIVE SCOPE</p><h3>{namespace || 'Select a namespace'}</h3></div>{namespace ? <Link className="button button-secondary" to="/namespaces">Manage resources</Link> : null}</div>{namespace ? <div className="admin-metric-grid"><article><strong>{files}</strong><span>files</span></article><article><strong>{keys}</strong><span>key-values</span></article><article><strong>{secrets}</strong><span>secret references</span></article><article><strong>{metadata?.lineage.length || 0}</strong><span>metadata ancestors</span></article></div> : <p className="inline-empty">Use the top-bar context selector to choose a namespace.</p>}</section>
      {metadata ? <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">INHERITANCE / PROVENANCE</p><h3>Workflow settings</h3></div></div><ol className="metadata-lineage">{metadata.lineage.map((scope) => <li key={scope.namespace}><div><strong>{scope.namespace}</strong><small>version {scope.resourceVersion} · {scope.updatedBy}</small></div><span>{scope.pluginDefaults.length} plugin defaults</span><ul>{scope.pluginDefaults.map((item) => <li key={`${scope.namespace}:${item.type}:${String(item.forced)}`}><code>{item.type}</code>{item.forced ? <b>forced</b> : null}<small>{Object.keys(item.values).join(', ') || 'no properties'}</small></li>)}</ul></li>)}</ol></section> : null}
    </div>
  </div>
}

function AccessAdministration({ api, tenant, principals, roles, bindings, providers, pending, mutate }: { api: ReturnType<typeof useApiClient>; tenant: string; principals: PrincipalDefinition[]; roles: Awaited<ReturnType<ReturnType<typeof useApiClient>['roles']>>; bindings: RoleBinding[]; providers: Awaited<ReturnType<ReturnType<typeof useApiClient>['providers']>>; pending: boolean; mutate: (operation: () => Promise<unknown>, message: string) => void }) {
  const [principalType, setPrincipalType] = useState<PrincipalDefinition['principal_type']>('USER')
  const [handle, setHandle] = useState('')
  const [display, setDisplay] = useState('')
  const [roleName, setRoleName] = useState('')
  const [roleDisplay, setRoleDisplay] = useState('')
  const [resource, setResource] = useState('flow')
  const [permission, setPermission] = useState('view')
  const [bindingPrincipal, setBindingPrincipal] = useState('')
  const [bindingRole, setBindingRole] = useState('viewer')
  const [bindingScope, setBindingScope] = useState<RoleBinding['scope_type']>('TENANT')
  const [bindingNamespace, setBindingNamespace] = useState('')
  const [group, setGroup] = useState('')
  const [member, setMember] = useState('')
  const [serviceAccount, setServiceAccount] = useState('')
  const [tokenName, setTokenName] = useState('control-plane')
  const [issuedToken, setIssuedToken] = useState('')
  const credentials = useQuery({ queryKey: ['admin', 'credentials', serviceAccount], queryFn: () => api.principalCredentials(serviceAccount), enabled: Boolean(serviceAccount) })
  if (pending) return <LoadingState label="Loading identities and authorization policy" />
  const submitPrincipal = (event: FormEvent) => { event.preventDefault(); mutate(() => api.createPrincipal(principalType, handle.trim(), display.trim()), `${principalType.replace('_', ' ').toLowerCase()} created`); setHandle(''); setDisplay('') }
  const submitRole = (event: FormEvent) => { event.preventDefault(); mutate(() => api.saveRole(roleName.trim(), roleDisplay.trim(), 'Created in the administration workbench.', [{ resource_type: resource.trim(), action: permission, effect: 'ALLOW' }]), 'Role saved'); setRoleName(''); setRoleDisplay('') }
  const submitBinding = (event: FormEvent) => { event.preventDefault(); const principal = principals.find((item) => item.id === bindingPrincipal); if (!principal) return; mutate(() => api.createBinding({ principal_id: principal.id, principal_type: principal.principal_type, role_name: bindingRole, scope_type: bindingScope, tenant_id: bindingScope === 'INSTANCE' ? null : tenant, namespace: bindingScope === 'NAMESPACE' ? bindingNamespace.trim() : null }), 'Binding created') }
  const issueToken = (event: FormEvent) => { event.preventDefault(); mutate(async () => { const issued = await api.createCredential(serviceAccount, tokenName.trim(), ['*:*'], expiryIn(30)); setIssuedToken(issued.token); return issued }, 'API token issued; copy it now') }
  return <div className="admin-section-stack">
    <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">IDENTITY PROVIDERS</p><h3>Configured entry points</h3></div><span>deployment configuration</span></div><div className="admin-card-grid">{providers.map((provider) => <article key={provider.id}><KeyRound size={18} aria-hidden="true" /><div><strong>{provider.display_name}</strong><small>{provider.kind} · {provider.interactive ? 'interactive' : 'non-interactive'}</small></div></article>)}</div></section>
    <div className="admin-split equal">
      <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">USERS / GROUPS / SERVICES</p><h3>Principals</h3></div><span>{principals.length}</span></div><form className="admin-form" onSubmit={submitPrincipal}><label>Type<select value={principalType} onChange={(event) => setPrincipalType(event.target.value as PrincipalDefinition['principal_type'])}><option>USER</option><option>GROUP</option><option>SERVICE_ACCOUNT</option></select></label><label>Handle<input value={handle} onChange={(event) => setHandle(event.target.value)} required pattern="[A-Za-z0-9][A-Za-z0-9_-]*" /></label><label>Display name<input value={display} onChange={(event) => setDisplay(event.target.value)} required /></label><button className="button button-primary" type="submit">Create principal</button></form><div className="compact-table"><table><thead><tr><th>Principal</th><th>Type</th><th>State</th></tr></thead><tbody>{principals.map((item) => <tr key={item.id}><td><strong>{item.display_name}</strong><small>{item.handle}</small></td><td>{item.principal_type}</td><td><StatusBadge state={item.enabled ? 'SUCCESS' : 'PAUSED'} /></td></tr>)}</tbody></table></div></section>
      <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">POLICY</p><h3>Roles</h3></div><span>{roles.length}</span></div><form className="admin-form" onSubmit={submitRole}><label>Role name<input value={roleName} onChange={(event) => setRoleName(event.target.value)} required /></label><label>Display name<input value={roleDisplay} onChange={(event) => setRoleDisplay(event.target.value)} required /></label><label>Resource<input value={resource} onChange={(event) => setResource(event.target.value)} required /></label><label>Action<select value={permission} onChange={(event) => setPermission(event.target.value)}><option>view</option><option>create</option><option>update</option><option>delete</option><option>execute</option><option>manage</option><option>use</option></select></label><button className="button button-primary" type="submit">Save role</button></form><div className="chip-list">{roles.map((item) => <span key={item.name}><strong>{item.name}</strong>{item.permissions.length} permissions{item.built_in ? ' · built in' : ''}</span>)}</div></section>
    </div>
    <div className="admin-split equal">
      <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">ASSIGNMENT</p><h3>Bindings & groups</h3></div><span>{bindings.length} bindings</span></div><form className="admin-form" onSubmit={submitBinding}><label>Principal<select value={bindingPrincipal} onChange={(event) => setBindingPrincipal(event.target.value)} required><option value="">Select</option>{principals.map((item) => <option key={item.id} value={item.id}>{item.handle}</option>)}</select></label><label>Role<select value={bindingRole} onChange={(event) => setBindingRole(event.target.value)}>{roles.map((item) => <option key={item.name}>{item.name}</option>)}</select></label><label>Scope<select value={bindingScope} onChange={(event) => setBindingScope(event.target.value as RoleBinding['scope_type'])}><option>INSTANCE</option><option>TENANT</option><option>NAMESPACE</option></select></label>{bindingScope === 'NAMESPACE' ? <label>Namespace<input value={bindingNamespace} onChange={(event) => setBindingNamespace(event.target.value)} required /></label> : null}<button className="button button-primary" type="submit">Create binding</button></form><form className="admin-form admin-inline-form" onSubmit={(event) => { event.preventDefault(); mutate(() => api.addGroupMember(group, member), 'Group membership added') }}><label>Group<select value={group} onChange={(event) => setGroup(event.target.value)} required><option value="">Select</option>{principals.filter((item) => item.principal_type === 'GROUP').map((item) => <option value={item.id} key={item.id}>{item.handle}</option>)}</select></label><label>Member<select value={member} onChange={(event) => setMember(event.target.value)} required><option value="">Select</option>{principals.filter((item) => item.id !== group && item.principal_type !== 'GROUP').map((item) => <option value={item.id} key={item.id}>{item.handle}</option>)}</select></label><button className="button button-secondary" type="submit">Add member</button></form></section>
      <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">SERVICE ACCOUNTS</p><h3>API tokens</h3></div><span>secret shown once</span></div><form className="admin-form" onSubmit={issueToken}><label>Service account<select value={serviceAccount} onChange={(event) => setServiceAccount(event.target.value)} required><option value="">Select</option>{principals.filter((item) => item.principal_type === 'SERVICE_ACCOUNT').map((item) => <option value={item.id} key={item.id}>{item.handle}</option>)}</select></label><label>Token name<input value={tokenName} onChange={(event) => setTokenName(event.target.value)} required /></label><button className="button button-primary" type="submit">Issue 30-day token</button></form>{issuedToken ? <div className="issued-secret" role="status"><AlertTriangle size={18} aria-hidden="true" /><div><strong>Copy this token now</strong><code>{issuedToken}</code></div></div> : null}<ul className="credential-list">{credentials.data?.map((item) => <li key={item.id}><strong>{item.name}</strong><span>{item.status} · expires {new Date(item.expires_at).toLocaleDateString()}</span></li>)}</ul></section>
    </div>
  </div>
}

function OperationsAdministration({ readiness, topology, workers, admission, search, pending }: { readiness?: Awaited<ReturnType<ReturnType<typeof useApiClient>['readiness']>>; topology?: Awaited<ReturnType<ReturnType<typeof useApiClient>['topology']>>; workers: Awaited<ReturnType<ReturnType<typeof useApiClient>['workers']>>; admission?: Awaited<ReturnType<ReturnType<typeof useApiClient>['admissionDiagnostics']>>; search?: Awaited<ReturnType<ReturnType<typeof useApiClient>['searchStatus']>>; pending: boolean }) {
  if (pending) return <LoadingState label="Loading component health" />
  const storage = topology?.quorumDependencies.objectStorage || 'not reported'
  return <div className="admin-section-stack">
    <section className="admin-health-strip"><article><Database aria-hidden="true" /><div><strong>PostgreSQL</strong><span>{readiness?.database || 'unknown'} · {readiness?.migrations_applied || 0}/{readiness?.migrations_expected || 0} migrations</span></div></article><article><Boxes aria-hidden="true" /><div><strong>Object storage</strong><span>{storage}</span></div></article><article><Network aria-hidden="true" /><div><strong>Queue</strong><span>{admission?.queued_requests || 0} queued · {admission?.active_reservations || 0} active</span></div></article><article><FileKey aria-hidden="true" /><div><strong>Search</strong><span>{search?.condition || 'unknown'} · {Math.round((search?.progress || 0) * 100)}% projected</span></div></article></section>
    <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">SERVICES</p><h3>Component topology</h3></div><span>{topology?.currentVersion || 'unknown'} · {topology?.coordination}</span></div><div className="admin-card-grid">{topology?.roles.map((role) => <article key={role.role}><div className={`health-dot health-${role.failoverStatus.toLowerCase()}`} /><div><strong>{role.role}</strong><small>{role.readyInstances}/{role.totalInstances} ready · {role.staleInstances} stale</small></div><b>{role.failoverStatus}</b></article>)}</div></section>
    <div className="admin-split equal"><section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">WORKERS</p><h3>Capacity</h3></div><span>{workers.length} workers</span></div>{workers.length ? <div className="compact-table"><table><thead><tr><th>Worker</th><th>Group</th><th>Utilization</th><th>State</th></tr></thead><tbody>{workers.map((worker) => <tr key={worker.worker_id}><td><strong>{worker.instance_name}</strong><small>{worker.version}</small></td><td>{worker.worker_group}</td><td>{Math.round(worker.utilization * 100)}%</td><td>{worker.liveness}</td></tr>)}</tbody></table></div> : <EmptyState title="No external workers" body="The local executor owns the current runnable workload." />}</section><section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">DATABASE / SEARCH</p><h3>Freshness</h3></div></div><dl className="admin-facts"><div><dt>Latest migration</dt><dd>{readiness?.latest_migration || 'none'}</dd></div><div><dt>Search documents</dt><dd>{formatNumber(search?.documentsIndexed || 0, 'en')}</dd></div><div><dt>Search source rows</dt><dd>{formatNumber(search?.sourceDocuments || 0, 'en')}</dd></div><div><dt>Search lag</dt><dd>{search?.lagSeconds == null ? 'unknown' : `${search.lagSeconds.toFixed(2)}s`}</dd></div><div><dt>Oldest queue age</dt><dd>{(admission?.oldest_queue_age_seconds || 0).toFixed(2)}s</dd></div></dl></section></div>
  </div>
}

function LifecycleAdministration({ api, tenant, namespace, policies, holds, jobs, pending, onChanged, onFailure }: { api: ReturnType<typeof useApiClient>; tenant: string; namespace: string; policies: LifecyclePolicy[]; holds: LifecycleLegalHold[]; jobs: LifecycleJob[]; pending: boolean; onChanged: (message: string) => Promise<void>; onFailure: (message: string) => void }) {
  const [resourceType, setResourceType] = useState<LifecycleResourceType>('EXECUTION')
  const [scope, setScope] = useState<LifecycleScope>('TENANT')
  const [policyNamespace, setPolicyNamespace] = useState(namespace)
  const [labelKey, setLabelKey] = useState('environment')
  const [labelValue, setLabelValue] = useState('production')
  const [retentionDays, setRetentionDays] = useState('30')
  const [batchSize, setBatchSize] = useState('100')
  const [scheduleMinutes, setScheduleMinutes] = useState('')
  const [policyReason, setPolicyReason] = useState('Apply the configured workflow data lifecycle')
  const [preview, setPreview] = useState<LifecycleJob | null>(null)
  const [confirmation, setConfirmation] = useState('')
  const [holdName, setHoldName] = useState('')
  const [holdReason, setHoldReason] = useState('')
  const [holdResourceId, setHoldResourceId] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (pending) return <LoadingState label="Loading lifecycle policies and purge evidence" />

  const createPolicy = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    try {
      await api.createLifecyclePolicy({
        resourceType,
        scope,
        namespace: scope === 'NAMESPACE' ? policyNamespace.trim() : null,
        labelSelector: scope === 'LABEL' ? { [labelKey.trim()]: labelValue.trim() } : {},
        retentionDays: Number(retentionDays),
        batchSize: Number(batchSize),
        scheduleIntervalMinutes: scheduleMinutes ? Number(scheduleMinutes) : null,
        enabled: true,
        reason: policyReason.trim(),
      })
      await onChanged('Lifecycle policy created')
    } catch (error) {
      onFailure(error instanceof Error ? error.message : String(error))
    } finally {
      setSubmitting(false)
    }
  }

  const previewPolicy = async (policy: LifecyclePolicy) => {
    try {
      const result = await api.previewLifecyclePurge(policy.id, `Manual ${policy.resourceType.toLowerCase()} lifecycle preview`)
      setPreview(result)
      setConfirmation('')
    } catch (error) {
      onFailure(error instanceof Error ? error.message : String(error))
    }
  }

  const executePreview = async () => {
    if (!preview) return
    setSubmitting(true)
    try {
      const result = await api.executeLifecycleJob(preview.id, confirmation)
      setPreview(null)
      setConfirmation('')
      await onChanged(`Lifecycle job ${result.state.toLowerCase()}`)
    } catch (error) {
      onFailure(error instanceof Error ? error.message : String(error))
    } finally {
      setSubmitting(false)
    }
  }

  const resumeJob = async (job: LifecycleJob) => {
    try {
      const result = await api.resumeLifecycleJob(job.id)
      await onChanged(`Lifecycle job resumed: ${result.state.toLowerCase()}`)
    } catch (error) {
      onFailure(error instanceof Error ? error.message : String(error))
    }
  }

  const createHold = async (event: FormEvent) => {
    event.preventDefault()
    try {
      await api.createLifecycleLegalHold({
        name: holdName.trim(),
        reason: holdReason.trim(),
        resourceType,
        resourceId: holdResourceId.trim() || null,
        namespace: scope === 'NAMESPACE' ? policyNamespace.trim() : null,
        labelSelector: scope === 'LABEL' ? { [labelKey.trim()]: labelValue.trim() } : {},
      })
      setHoldName('')
      setHoldReason('')
      setHoldResourceId('')
      await onChanged('Lifecycle legal hold created')
    } catch (error) {
      onFailure(error instanceof Error ? error.message : String(error))
    }
  }

  return <div className="admin-section-stack">
    <section className="admin-panel">
      <div className="section-heading"><div><p className="eyebrow">POLICY / SCHEDULE</p><h3>Retention boundaries</h3><p>Specific namespace and label policies override broader operator intent during selection.</p></div><span>{tenant} · {policies.length} policies</span></div>
      <form className="admin-form" onSubmit={(event) => void createPolicy(event)}>
        <label>Resource<select value={resourceType} onChange={(event) => setResourceType(event.target.value as LifecycleResourceType)}><option>EXECUTION</option><option>LOG</option><option>METRIC</option><option>ARTIFACT</option><option>CACHE</option></select></label>
        <label>Scope<select value={scope} onChange={(event) => setScope(event.target.value as LifecycleScope)}><option>INSTANCE</option><option>TENANT</option><option>NAMESPACE</option><option>LABEL</option></select></label>
        {scope === 'NAMESPACE' ? <label>Namespace<input value={policyNamespace} onChange={(event) => setPolicyNamespace(event.target.value)} required /></label> : null}
        {scope === 'LABEL' ? <><label>Label key<input value={labelKey} onChange={(event) => setLabelKey(event.target.value)} required /></label><label>Label value<input value={labelValue} onChange={(event) => setLabelValue(event.target.value)} required /></label></> : null}
        <label>Retention days<input type="number" min="1" max="36500" value={retentionDays} onChange={(event) => setRetentionDays(event.target.value)} required /></label>
        <label>Batch size<input type="number" min="1" max="1000" value={batchSize} onChange={(event) => setBatchSize(event.target.value)} required /></label>
        <label>Schedule minutes<input type="number" min="5" max="525600" value={scheduleMinutes} onChange={(event) => setScheduleMinutes(event.target.value)} placeholder="Manual only" /></label>
        <label className="span-two">Reason<input minLength={3} maxLength={2048} value={policyReason} onChange={(event) => setPolicyReason(event.target.value)} required /></label>
        <button className="button button-primary" type="submit" disabled={submitting}>Create policy</button>
      </form>
      {policies.length ? <div className="table-shell"><table><thead><tr><th>Resource</th><th>Scope</th><th>Retention</th><th>Batch / schedule</th><th>Next run</th><th>Action</th></tr></thead><tbody>{policies.map((policy) => <tr key={policy.id}><td><strong>{policy.resourceType}</strong><small>{policy.reason}</small></td><td>{policy.scope}<small>{policy.namespace || Object.entries(policy.labelSelector).map(([key, value]) => `${key}=${value}`).join(', ') || policy.tenantId || 'instance'}</small></td><td>{policy.retentionDays} days</td><td>{policy.batchSize}<small>{policy.scheduleIntervalMinutes ? `every ${policy.scheduleIntervalMinutes}m` : 'manual'}</small></td><td>{policy.nextRunAt ? formatDate(policy.nextRunAt, 'en', 'UTC') : '—'}</td><td><button className="button button-secondary" type="button" onClick={() => void previewPolicy(policy)}>Preview purge</button></td></tr>)}</tbody></table></div> : <EmptyState title="No lifecycle policies" body="Create a resource-scoped policy before previewing a purge." />}
    </section>
    <div className="admin-split equal">
      <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">LEGAL HOLDS</p><h3>Protected evidence</h3></div><span>{holds.filter((hold) => hold.active).length} active</span></div><form className="admin-form" onSubmit={(event) => void createHold(event)}><label>Name<input value={holdName} onChange={(event) => setHoldName(event.target.value)} required /></label><label>Resource ID<input value={holdResourceId} onChange={(event) => setHoldResourceId(event.target.value)} placeholder="Optional execution or record ID" /></label><label className="span-two">Reason<input value={holdReason} onChange={(event) => setHoldReason(event.target.value)} minLength={3} required /></label><button className="button button-primary" type="submit">Create hold</button></form><div className="chip-list">{holds.map((hold) => <span key={hold.id}><strong>{hold.name}</strong>{hold.resourceType || 'ALL'} · {hold.active ? 'active' : 'released'}{hold.active ? <button className="button button-quiet" type="button" onClick={() => void api.releaseLifecycleLegalHold(hold.id).then(() => onChanged('Lifecycle legal hold released')).catch((error: Error) => onFailure(error.message))}>Release</button> : null}</span>)}</div></section>
      <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">PROGRESS / EVIDENCE</p><h3>Purge jobs</h3></div><span>{jobs.length} recent</span></div>{jobs.length ? <div className="compact-table"><table><thead><tr><th>Job</th><th>Progress</th><th>State</th><th>Action</th></tr></thead><tbody>{jobs.map((job) => <tr key={job.id}><td><strong>{job.policySnapshot.resourceType}</strong><small>{job.trigger} · {formatDate(job.createdAt, 'en', 'UTC')}</small></td><td>{formatNumber(job.processedRecords, 'en')} / {formatNumber(job.estimatedRecords, 'en')}<small>{formatNumber(job.processedBytes, 'en')} bytes · {job.retryCount} retries</small></td><td><StatusBadge state={job.state} />{job.lastError ? <small>{job.lastError}</small> : null}</td><td>{['READY', 'RUNNING', 'WAITING_EXTERNAL', 'FAILED'].includes(job.state) ? <button className="button button-secondary" type="button" onClick={() => void resumeJob(job)}>Resume batch</button> : '—'}</td></tr>)}</tbody></table></div> : <EmptyState title="No purge jobs" body="Impact previews and scheduled sweeps appear here with durable progress evidence." />}</section>
    </div>
    {preview ? <div className="modal-backdrop"><section className="confirmation-dialog admin-impact-dialog" role="dialog" aria-modal="true" aria-labelledby="lifecycle-impact-title"><p className="eyebrow">DESTRUCTIVE IMPACT PREVIEW</p><h2 id="lifecycle-impact-title">Confirm {preview.policySnapshot.resourceType.toLowerCase()} purge</h2><div className="impact-grid"><article><strong>Impact</strong><ul><li>{formatNumber(preview.estimatedRecords, 'en')} records</li><li>{formatNumber(preview.estimatedBytes, 'en')} bytes</li><li>{formatNumber(preview.activeRecords, 'en')} active records excluded</li><li>{formatNumber(preview.protectedRecords, 'en')} legal-held records protected</li></ul></article><article><strong>Recovery consequences</strong><p>Authoritative metadata decisions, object deletions and search projection removal are irreversible without a qualified backup restore.</p></article></div><p className="approval-expiry"><AlertTriangle size={16} aria-hidden="true" />Preview expires {new Date(preview.previewExpiresAt).toLocaleTimeString()}.</p><label>Type <code>{preview.confirmationPhrase}</code><input autoFocus value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label><div><button className="button button-secondary" type="button" onClick={() => setPreview(null)}>Cancel</button><button className="button button-danger" type="button" disabled={confirmation !== preview.confirmationPhrase || submitting} onClick={() => void executePreview()}>Purge one bounded batch</button></div></section></div> : null}
  </div>
}

function ControlsAdministration({ controls, flags, announcements, operationalControls, api, tenant, namespace, pending, onChanged, onFailure }: { controls: AdministrationControl[]; flags: Awaited<ReturnType<ReturnType<typeof useApiClient>['featureFlags']>>; announcements: Announcement[]; operationalControls: OperationalControl[]; api: ReturnType<typeof useApiClient>; tenant: string; namespace: string; pending: boolean; onChanged: (message: string) => Promise<void>; onFailure: (message: string) => void }) {
  const [selected, setSelected] = useState<AdministrationControl | null>(null)
  const [enabled, setEnabled] = useState(false)
  const [value, setValue] = useState('')
  const [reason, setReason] = useState('')
  const [preview, setPreview] = useState<AdministrationImpactPreview | null>(null)
  const [confirmation, setConfirmation] = useState('')
  const [flagKey, setFlagKey] = useState('')
  const [flagEnabled, setFlagEnabled] = useState(false)
  const [flagDescription, setFlagDescription] = useState('')
  const previewMutation = useMutation({ mutationFn: (draft: AdministrationControlDraft) => api.previewAdministrationControl(draft), onSuccess: setPreview, onError: (error) => onFailure(error.message) })
  const applyMutation = useMutation({ mutationFn: ({ impact, phrase }: { impact: AdministrationImpactPreview; phrase: string }) => api.applyAdministrationControl(impact, phrase), onSuccess: async () => { setPreview(null); setSelected(null); setConfirmation(''); await onChanged('Administrative control applied and audited') }, onError: async (error) => { onFailure(error.message); await onChanged('Rejected administrative action recorded in audit history') } })
  if (pending) return <LoadingState label="Loading administrative controls" />
  const edit = (control: AdministrationControl) => { setSelected(control); setEnabled(control.enabled); setValue(control.value == null ? '' : String(control.value)); setReason(''); setPreview(null) }
  const submit = (event: FormEvent) => { event.preventDefault(); if (!selected) return; try { previewMutation.mutate(administrationControlDraft(selected, enabled, value, reason)) } catch (error) { onFailure(error instanceof Error ? error.message : 'Invalid control') } }
  return <div className="admin-section-stack">
    <p className="admin-safety-note"><ShieldCheck size={18} aria-hidden="true" /><span><strong>Guarded changes</strong> Every control requires a server-generated impact preview, a short-lived actor/tenant-bound approval, exact confirmation and immutable success or rejection evidence.</span></p>
    <OperationalPosture announcements={announcements} controls={operationalControls} api={api} namespace={namespace} onChanged={onChanged} onFailure={onFailure} />
    <section className="admin-control-grid">{controls.map((control) => { const copy = CONTROL_COPY[control.key]; return <article key={control.key} className={control.enabled ? 'enabled' : ''}><header><div><p className="eyebrow">{control.key.replace('_', ' ')}</p><h3>{copy.title}</h3></div><StatusBadge state={control.enabled ? 'RUNNING' : 'PAUSED'} /></header><p>{copy.summary}</p>{copy.valueLabel ? <dl><dt>{copy.valueLabel}</dt><dd>{control.value || '—'}</dd></dl> : null}<footer><span>{control.version ? `v${String(control.version)} · ${control.updatedBy || 'unknown'}` : 'default policy'}</span><button className="button button-secondary" type="button" onClick={() => edit(control)}>Preview change</button></footer></article> })}</section>
    {selected ? <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">DRAFT</p><h3>{CONTROL_COPY[selected.key].title}</h3></div><button className="button button-quiet" type="button" onClick={() => setSelected(null)}>Close</button></div><form className="admin-form control-form" onSubmit={submit}><label className="toggle-field"><input type="checkbox" checked={enabled} onChange={(event) => setEnabled(event.target.checked)} /><span>{enabled ? 'Enabled' : 'Disabled'}</span></label>{selected.key === 'RETENTION' ? <label>Days<input type="number" min="1" max="3650" value={value} onChange={(event) => setValue(event.target.value)} required /></label> : null}{selected.key === 'ANNOUNCEMENT' ? <label className="span-two">Message<textarea value={value} onChange={(event) => setValue(event.target.value)} maxLength={1000} required={enabled} /></label> : null}<label className="span-two">Reason<input value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Why is this change required?" minLength={3} required /></label><button className="button button-primary" type="submit">Generate impact preview</button></form></section> : null}
    <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">FEATURE FLAGS</p><h3>Scoped release controls</h3></div><span>{tenant} · {flags.length} visible</span></div><form className="admin-form" onSubmit={(event) => { event.preventDefault(); const key = flagKey.trim(); if (key.startsWith('admin-')) { onFailure('Keys beginning with admin- require the guarded control workflow.'); return } void api.saveFeatureFlag(key, flagEnabled, flagDescription).then(() => { setFlagKey(''); setFlagDescription(''); return onChanged('Feature flag saved') }).catch((error: Error) => onFailure(error.message)) }}><label>Key<input value={flagKey} onChange={(event) => setFlagKey(event.target.value)} required pattern="[A-Za-z0-9][A-Za-z0-9_-]*" /></label><label className="toggle-field"><input type="checkbox" checked={flagEnabled} onChange={(event) => setFlagEnabled(event.target.checked)} /><span>{flagEnabled ? 'Enabled' : 'Disabled'}</span></label><label className="span-two">Description<input value={flagDescription} onChange={(event) => setFlagDescription(event.target.value)} /></label><button className="button button-primary" type="submit">Save flag</button></form><div className="chip-list">{flags.filter((flag) => !flag.key.startsWith('admin-')).map((flag) => <span key={`${flag.scope}:${flag.key}`}><strong>{flag.key}</strong>{flag.scope} · {flag.enabled ? 'on' : 'off'} · v{flag.version}</span>)}</div></section>
    {preview ? <div className="modal-backdrop"><section className="confirmation-dialog admin-impact-dialog" role="dialog" aria-modal="true" aria-labelledby="admin-impact-title"><p className="eyebrow">SHORT-LIVED STEP-UP APPROVAL</p><h2 id="admin-impact-title">Confirm {CONTROL_COPY[preview.draft.key].title}</h2><div className="impact-grid"><article><strong>Impact</strong><ul>{preview.impacts.map((item) => <li key={item}>{item}</li>)}</ul></article><article><strong>Recovery</strong><p>{preview.recovery}</p></article></div><p className="approval-expiry"><AlertTriangle size={16} aria-hidden="true" />Approval expires {new Date(preview.expiresAt).toLocaleTimeString()}.</p><label>Type <code>{preview.confirmation}</code><input autoFocus value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label><div><button className="button button-secondary" type="button" onClick={() => setPreview(null)}>Cancel</button><button className="button button-danger" type="button" disabled={confirmation !== preview.confirmation || applyMutation.isPending} onClick={() => applyMutation.mutate({ impact: preview, phrase: confirmation })}>Apply guarded change</button></div></section></div> : null}
  </div>
}

const operationalBoundaries: OperationalBoundary[] = ['AUTHORING', 'NEW_EXECUTIONS', 'TRIGGERS', 'API_WRITES', 'WORKER_DISPATCH']

function OperationalPosture({ announcements, controls, api, namespace, onChanged, onFailure }: { announcements: Announcement[]; controls: OperationalControl[]; api: ReturnType<typeof useApiClient>; namespace: string; onChanged: (message: string) => Promise<void>; onFailure: (message: string) => void }) {
  const [announcementTitle, setAnnouncementTitle] = useState('')
  const [announcementMessage, setAnnouncementMessage] = useState('')
  const [announcementSeverity, setAnnouncementSeverity] = useState<AnnouncementSeverity>('INFO')
  const [announcementAudience, setAnnouncementAudience] = useState<AnnouncementAudience>('TENANT')
  const [announcementHours, setAnnouncementHours] = useState(4)
  const [controlKind, setControlKind] = useState<OperationalControl['kind']>('MAINTENANCE')
  const [controlName, setControlName] = useState('')
  const [controlScope, setControlScope] = useState<OperationalControlScope>('TENANT')
  const [controlNamespace, setControlNamespace] = useState(namespace)
  const [controlFlow, setControlFlow] = useState('')
  const [controlPlugin, setControlPlugin] = useState('')
  const [controlRunner, setControlRunner] = useState('')
  const [boundaries, setBoundaries] = useState<OperationalBoundary[]>(['NEW_EXECUTIONS', 'TRIGGERS'])
  const [runningPolicy, setRunningPolicy] = useState<OperationalControl['runningWorkPolicy']>('DRAIN')
  const [controlReason, setControlReason] = useState('')
  const [controlHours, setControlHours] = useState(1)
  const [submitting, setSubmitting] = useState(false)

  const submitAnnouncement = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    try {
      await api.publishAnnouncement({
        title: announcementTitle.trim(),
        message: announcementMessage.trim(),
        severity: announcementSeverity,
        audience: announcementAudience,
        namespace: announcementAudience === 'NAMESPACE' ? controlNamespace.trim() : null,
        startsAt: new Date().toISOString(),
        expiresAt: hoursFromNow(announcementHours),
      })
      setAnnouncementTitle('')
      setAnnouncementMessage('')
      await onChanged('Announcement published')
    } catch (error) {
      onFailure(error instanceof Error ? error.message : 'Could not publish announcement')
    } finally {
      setSubmitting(false)
    }
  }

  const submitControl = async (event: FormEvent) => {
    event.preventDefault()
    if (!boundaries.length) {
      onFailure('Select at least one enforcement boundary.')
      return
    }
    setSubmitting(true)
    try {
      await api.activateOperationalControl({
        kind: controlKind,
        name: controlName.trim(),
        scope: controlScope,
        namespace: ['NAMESPACE', 'FLOW'].includes(controlScope) ? controlNamespace.trim() : null,
        flowId: controlScope === 'FLOW' ? controlFlow.trim() : null,
        pluginId: controlScope === 'PLUGIN' ? controlPlugin.trim() : null,
        runnerId: controlScope === 'RUNNER' ? controlRunner.trim() : null,
        boundaries,
        runningWorkPolicy: runningPolicy,
        reason: controlReason.trim(),
        expiresAt: hoursFromNow(controlHours),
      })
      setControlName('')
      setControlReason('')
      await onChanged('Operational control activated and propagation started')
    } catch (error) {
      onFailure(error instanceof Error ? error.message : 'Could not activate control')
    } finally {
      setSubmitting(false)
    }
  }

  const changeControl = async (control: OperationalControl, action: 'EXTEND' | 'BYPASS' | 'DEACTIVATE') => {
    const reason = window.prompt(`${action.replace('_', ' ').toLowerCase()} reason`)
    if (!reason?.trim()) return
    try {
      await api.changeOperationalControl(control.id, {
        action,
        reason: reason.trim(),
        expectedVersion: control.version,
        ...(action === 'EXTEND' ? { expiresAt: hoursFromNow(1) } : {}),
        ...(action === 'BYPASS' ? { bypassUntil: hoursFromNow(0.25) } : {}),
      })
      await onChanged(`Operational control ${action.toLowerCase()} recorded`)
    } catch (error) {
      onFailure(error instanceof Error ? error.message : 'Could not change control')
    }
  }

  return (
    <div className="admin-section-stack operational-posture">
      <div className="admin-split equal">
        <section className="admin-panel">
          <div className="section-heading">
            <div><p className="eyebrow">SCHEDULED / IMMEDIATE</p><h3>Announcements</h3></div>
            <span>{announcements.filter((item) => item.active).length} active</span>
          </div>
          <form className="admin-form" onSubmit={(event) => void submitAnnouncement(event)}>
            <label>Title<input value={announcementTitle} onChange={(event) => setAnnouncementTitle(event.target.value)} required maxLength={200} /></label>
            <label>Severity<select value={announcementSeverity} onChange={(event) => setAnnouncementSeverity(event.target.value as AnnouncementSeverity)}><option>INFO</option><option>WARNING</option><option>CRITICAL</option></select></label>
            <label>Audience<select value={announcementAudience} onChange={(event) => setAnnouncementAudience(event.target.value as AnnouncementAudience)}><option>TENANT</option><option>NAMESPACE</option><option>INSTANCE</option></select></label>
            <label>Expires in hours<input type="number" min="1" max="720" value={announcementHours} onChange={(event) => setAnnouncementHours(Number(event.target.value))} /></label>
            {announcementAudience === 'NAMESPACE' ? <label className="span-two">Namespace<input value={controlNamespace} onChange={(event) => setControlNamespace(event.target.value)} required /></label> : null}
            <label className="span-two">Message<textarea value={announcementMessage} onChange={(event) => setAnnouncementMessage(event.target.value)} required maxLength={4000} /></label>
            <button className="button button-primary" type="submit" disabled={submitting}>Publish announcement</button>
          </form>
          <div className="operational-list">
            {announcements.map((announcement) => <article key={announcement.id}><div><strong>{announcement.title}</strong><small>{announcement.severity} · {announcement.audience} · expires {new Date(announcement.expiresAt).toLocaleString()}</small><p>{announcement.message}</p></div><StatusBadge state={announcement.active ? 'RUNNING' : 'PAUSED'} />{announcement.active ? <button className="button button-quiet" type="button" onClick={() => void api.deactivateAnnouncement(announcement.id, announcement.version).then(() => onChanged('Announcement deactivated')).catch((error: Error) => onFailure(error.message))}>Deactivate</button> : null}</article>)}
          </div>
        </section>
        <section className="admin-panel">
          <div className="section-heading">
            <div><p className="eyebrow">DURABLE ENFORCEMENT</p><h3>Maintenance & kill switches</h3></div>
            <span>{controls.filter((item) => item.state === 'ACTIVE').length} active</span>
          </div>
          <form className="admin-form" onSubmit={(event) => void submitControl(event)}>
            <label>Kind<select value={controlKind} onChange={(event) => setControlKind(event.target.value as OperationalControl['kind'])}><option>MAINTENANCE</option><option>KILL_SWITCH</option></select></label>
            <label>Name<input value={controlName} onChange={(event) => setControlName(event.target.value)} required /></label>
            <label>Scope<select value={controlScope} onChange={(event) => setControlScope(event.target.value as OperationalControlScope)}>{(['TENANT', 'NAMESPACE', 'FLOW', 'PLUGIN', 'RUNNER', 'INSTANCE'] as OperationalControlScope[]).map((scope) => <option key={scope}>{scope}</option>)}</select></label>
            <label>Running work<select value={runningPolicy} onChange={(event) => setRunningPolicy(event.target.value as OperationalControl['runningWorkPolicy'])}><option>CONTINUE</option><option>DRAIN</option><option>CANCEL</option></select></label>
            {['NAMESPACE', 'FLOW'].includes(controlScope) ? <label>Namespace<input value={controlNamespace} onChange={(event) => setControlNamespace(event.target.value)} required /></label> : null}
            {controlScope === 'FLOW' ? <label>Flow ID<input value={controlFlow} onChange={(event) => setControlFlow(event.target.value)} required /></label> : null}
            {controlScope === 'PLUGIN' ? <label>Plugin ID<input value={controlPlugin} onChange={(event) => setControlPlugin(event.target.value)} required /></label> : null}
            {controlScope === 'RUNNER' ? <label>Runner ID<input value={controlRunner} onChange={(event) => setControlRunner(event.target.value)} required placeholder="local, docker or kubernetes" /></label> : null}
            <fieldset className="span-two"><legend>Enforcement boundaries</legend><div className="control-boundaries">{operationalBoundaries.map((boundary) => <label key={boundary}><input type="checkbox" checked={boundaries.includes(boundary)} onChange={(event) => setBoundaries((current) => event.target.checked ? [...current, boundary] : current.filter((item) => item !== boundary))} />{boundary.replace('_', ' ')}</label>)}</div></fieldset>
            <label>Expires in hours<input type="number" min="1" max="720" value={controlHours} onChange={(event) => setControlHours(Number(event.target.value))} /></label>
            <label className="span-two">Reason<input value={controlReason} onChange={(event) => setControlReason(event.target.value)} minLength={3} required /></label>
            <button className="button button-danger" type="submit" disabled={submitting}>Activate control</button>
          </form>
        </section>
      </div>
      <section className="admin-panel">
        <div className="section-heading"><div><p className="eyebrow">PROPAGATION / RUNNING-WORK POLICY</p><h3>Control status</h3></div><span>{controls.length} controls</span></div>
        <div className="table-shell"><table><thead><tr><th>Control</th><th>Scope</th><th>Boundaries</th><th>Policy</th><th>Acknowledged</th><th>Actions</th></tr></thead><tbody>{controls.map((control) => <tr key={control.id}><td><strong>{control.name}</strong><small>{control.kind} · <StatusBadge state={control.state === 'ACTIVE' ? 'RUNNING' : control.state === 'BYPASSED' ? 'WARNING' : 'PAUSED'} /></small></td><td>{control.scope}<small>{control.namespace || control.flowId || control.pluginId || control.runnerId || 'all'}</small></td><td>{control.boundaries.join(', ')}</td><td>{control.runningWorkPolicy}</td><td>{control.acknowledgements.length}<small>{control.acknowledgements.map((ack) => ack.componentRole).join(', ') || 'waiting'}</small></td><td>{control.state === 'ACTIVE' ? <div className="table-actions"><button className="button button-quiet" type="button" onClick={() => void changeControl(control, 'EXTEND')}>Extend</button><button className="button button-quiet" type="button" onClick={() => void changeControl(control, 'BYPASS')}>Bypass</button><button className="button button-danger" type="button" onClick={() => void changeControl(control, 'DEACTIVATE')}>Deactivate</button></div> : '—'}</td></tr>)}</tbody></table></div>
      </section>
    </div>
  )
}

function ConfigurationAdministration({ snapshot, pending, onReload }: { snapshot?: Awaited<ReturnType<ReturnType<typeof useApiClient>['configuration']>>; pending: boolean; onReload: () => void }) {
  const [query, setQuery] = useState('')
  const entries = useMemo(() => visibleConfiguration(snapshot?.entries || [], query), [query, snapshot?.entries])
  if (pending) return <LoadingState label="Loading effective configuration" />
  if (!snapshot) return <EmptyState title="Configuration unavailable" body="The effective configuration endpoint returned no snapshot." />
  return <section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">EFFECTIVE / REDACTED</p><h3>Configuration version {snapshot.version}</h3><p>{snapshot.fingerprint.slice(0, 16)} · loaded {new Date(snapshot.loaded_at).toLocaleString()}</p></div><button className="button button-secondary" type="button" onClick={() => { if (window.confirm('Reload only settings marked reloadable? Rejected changes are audited.')) onReload() }}><RefreshCw size={16} aria-hidden="true" />Reload</button></div><div className="configuration-toolbar"><label>Filter configuration<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="setting or source" /></label><span><ShieldCheck size={15} aria-hidden="true" />Secret values are server-redacted</span></div><div className="table-shell"><table><thead><tr><th>Setting</th><th>Effective value</th><th>Provenance</th><th>Reload</th></tr></thead><tbody>{entries.map((entry) => <tr key={entry.name}><td><strong>{entry.name}</strong>{entry.secret ? <small className="cell-subtitle">sensitive</small> : null}</td><td><code className="config-value">{configurationValue(entry)}</code></td><td>{entry.source}</td><td>{entry.reloadable ? 'live' : 'restart'}</td></tr>)}</tbody></table></div></section>
}

function AuditAdministration({ direct, indexed, pending, settings }: { direct: Awaited<ReturnType<ReturnType<typeof useApiClient>['administrationAudit']>>; indexed: Awaited<ReturnType<ReturnType<typeof useApiClient>['search']>>['items']; pending: boolean; settings: ReturnType<typeof useAppSettings>['settings'] }) {
  if (pending) return <LoadingState label="Loading administration audit history" />
  return <div className="admin-section-stack"><section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">IMMEDIATE CONTROL DECISIONS</p><h3>Successful and rejected changes</h3></div><span>{direct.length} events</span></div>{direct.length ? <div className="table-shell"><table><thead><tr><th>Time</th><th>Control</th><th>Outcome</th><th>Actor</th><th>Reason</th></tr></thead><tbody>{direct.map((event) => <tr key={event.eventId}><td><time dateTime={event.occurredAt}>{formatDate(event.occurredAt, settings.locale, settings.timezone)}</time></td><td><strong>{event.resourceId}</strong><small className="cell-subtitle">{event.action}</small></td><td><StatusBadge state={event.outcome === 'SUCCESS' ? 'SUCCESS' : 'FAILED'} /></td><td><code>{event.actorId.slice(0, 12)}</code></td><td>{event.reason}</td></tr>)}</tbody></table></div> : <EmptyState title="No guarded control actions" body="Preview and apply or reject a control change to create immediate evidence." />}</section><section className="admin-panel"><div className="section-heading"><div><p className="eyebrow">INDEXED AUDIT LEDGER</p><h3>All administration resources</h3></div><span>{indexed.length} projected events</span></div><div className="audit-list">{indexed.map((event) => <article key={event.documentId}><ScrollText size={17} aria-hidden="true" /><div><strong>{fieldText(event.fields.action, event.title)}</strong><p>{event.summary}</p><small>{fieldText(event.fields.resourceType, 'resource')} · {fieldText(event.fields.outcome, event.state || 'recorded')} · {formatDate(event.occurredAt, settings.locale, settings.timezone)}</small></div></article>)}</div></section></div>
}
