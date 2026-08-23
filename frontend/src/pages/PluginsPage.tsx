import { useState, type FormEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { BadgeCheck, Ban, Code2, Download, FileCheck2, FlaskConical, PackageCheck, RefreshCw, ShieldCheck, Trash2 } from 'lucide-react'

import type { PluginPolicyRuleDraft, PluginPolicyStage, PluginQuarantineDraft, UiSession } from '../api/types'
import { formatDate } from '../app/format'
import { useApiClient, usePluginPolicy, usePluginRegistry } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'

const POLICY_STAGES: PluginPolicyStage[] = ['AUTHORING', 'VALIDATION', 'EXECUTION', 'ADMINISTRATION']

export function PluginsPage({ session }: { session: UiSession }) {
  const registry = usePluginRegistry()
  const policy = usePluginPolicy()
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const canManage = session.capabilities['administration.manage']
  const [notice, setNotice] = useState('')
  const [ruleDraft, setRuleDraft] = useState<PluginPolicyRuleDraft>({
    scope: settings.namespace ? 'NAMESPACE' : 'TENANT',
    namespace: settings.namespace || null,
    effect: 'ALLOW',
    stages: ['AUTHORING', 'VALIDATION', 'EXECUTION'],
    selector: { package: '*', versionRange: '*', vendor: '*', pluginTypes: [], capabilities: [] },
    priority: 0,
    reason: 'Approved for this workspace',
    enabled: true,
  })
  const [quarantineDraft, setQuarantineDraft] = useState<PluginQuarantineDraft>({ scope: 'INSTANCE', package: '', version: '', reason: '' })
  const [impact, setImpact] = useState<Awaited<ReturnType<typeof api.previewPluginQuarantine>> | null>(null)
  const refreshPolicy = async () => { await queryClient.invalidateQueries({ queryKey: ['plugin-policy'] }) }
  const createRule = useMutation({
    mutationFn: api.createPluginPolicyRule,
    onSuccess: async () => { setNotice('Policy rule saved and active.'); await refreshPolicy() },
  })
  const deleteRule = useMutation({
    mutationFn: api.deletePluginPolicyRule,
    onSuccess: async () => { setNotice('Policy rule deleted.'); await refreshPolicy() },
  })
  const previewQuarantine = useMutation({
    mutationFn: api.previewPluginQuarantine,
    onSuccess: setImpact,
  })
  const createQuarantine = useMutation({
    mutationFn: api.createPluginQuarantine,
    onSuccess: async () => { setImpact(null); setNotice('Plugin version disabled. Historical pins are retained.'); await refreshPolicy() },
  })
  const packages = registry.data?.packages || []
  const totals = packages.reduce(
    (current, release) => ({
      active: current.active + (release.yanked ? 0 : 1),
      certified: current.certified + (release.signals.certification === 'certified' ? 1 : 0),
      current: current.current + (release.signals.security === 'current' ? 1 : 0),
      yanked: current.yanked + (release.yanked ? 1 : 0),
    }),
    { active: 0, certified: 0, current: 0, yanked: 0 },
  )

  return (
    <div className="page-stack">
      <header className="page-heading">
        <div>
          <p className="eyebrow">EXTEND / SUPPLY CHAIN</p>
          <h1>Plugin registry</h1>
          <p>Signed immutable releases, provenance evidence and adoption signals from the self-hosted registry.</p>
        </div>
        <button className="button button-secondary" type="button" onClick={() => void registry.refetch()} disabled={registry.isFetching}>
          <RefreshCw className={registry.isFetching ? 'spin' : ''} size={17} aria-hidden="true" />
          Refresh
        </button>
      </header>

      <section className="metric-strip" aria-label="Plugin registry summary">
        <article><span><PackageCheck size={16} aria-hidden="true" />Available</span><strong>{totals.active}</strong><small>immutable releases</small></article>
        <article><span><FileCheck2 size={16} aria-hidden="true" />Certified</span><strong>{totals.certified}</strong><small>informational status</small></article>
        <article><span><ShieldCheck size={16} aria-hidden="true" />Security current</span><strong>{totals.current}</strong><small>published reports</small></article>
        <article className={totals.yanked ? 'metric-alert' : ''}><span><Ban size={16} aria-hidden="true" />Yanked</span><strong>{totals.yanked}</strong><small>history retained</small></article>
      </section>

      <p className="registry-disclaimer"><ShieldCheck size={17} aria-hidden="true" />Popularity, maintenance, certification and security labels are informational signals—not trust guarantees. Verify signed evidence before adoption.</p>

      <section className="developer-portal plugin-governance" aria-labelledby="plugin-governance-heading">
        <div className="section-heading">
          <div><p className="eyebrow">GOVERN / EXPLAIN / DISABLE</p><h2 id="plugin-governance-heading">Effective plugin policy</h2></div>
          <ShieldCheck size={22} aria-hidden="true" />
        </div>
        {policy.isPending ? <LoadingState label="Loading effective plugin policy" /> : null}
        {policy.error ? <ErrorState message={policy.error.message} retry={() => void policy.refetch()} /> : null}
        {policy.data ? (
          <>
            <div className="policy-summary">
              <span>Unmatched third-party packages</span><StatusBadge state={policy.data.defaultEffect === 'ALLOW' ? 'PASS' : 'FAIL'} />
              <strong>{policy.data.defaultEffect}</strong><small>{policy.data.namespace ? `Namespace ${policy.data.namespace}` : 'Tenant and instance policy'}</small>
            </div>
            <div className="policy-rule-list" aria-label="Effective plugin policy rules">
              {policy.data.rules.length ? policy.data.rules.map((rule) => (
                <article key={rule.id}>
                  <div><StatusBadge state={rule.effect === 'ALLOW' ? 'PASS' : 'FAIL'} /><strong>{rule.selector.package}</strong><code>{rule.selector.versionRange}</code></div>
                  <p>{rule.reason}</p>
                  <small>{rule.scope}{rule.namespace ? ` / ${rule.namespace}` : ''} · {rule.stages.join(', ')} · source {rule.id.slice(0, 8)}</small>
                  {canManage ? <button className="icon-button" type="button" aria-label={`Delete policy for ${rule.selector.package}`} onClick={() => deleteRule.mutate(rule.id)}><Trash2 size={15} /></button> : null}
                </article>
              )) : <p className="muted-copy">No explicit rules. Embedded core plugins are allowed; the displayed default applies to unmatched third-party packages.</p>}
            </div>
            {policy.data.quarantines.filter((item) => item.state === 'ACTIVE').length ? (
              <div className="active-quarantines" aria-label="Active plugin quarantines">
                {policy.data.quarantines.filter((item) => item.state === 'ACTIVE').map((item) => <span key={item.id}><Ban size={14} />{item.package}@{item.version} · {item.reason}</span>)}
              </div>
            ) : null}
          </>
        ) : null}
        {canManage ? (
          <div className="governance-forms">
            <form onSubmit={(event: FormEvent) => { event.preventDefault(); createRule.mutate({ ...ruleDraft, namespace: ruleDraft.scope === 'NAMESPACE' ? settings.namespace : null }) }}>
              <h3>Add allow or deny rule</h3>
              <label>Effect<select value={ruleDraft.effect} onChange={(event) => setRuleDraft({ ...ruleDraft, effect: event.target.value as 'ALLOW' | 'DENY' })}><option>ALLOW</option><option>DENY</option></select></label>
              <label>Scope<select value={ruleDraft.scope} onChange={(event) => setRuleDraft({ ...ruleDraft, scope: event.target.value as PluginPolicyRuleDraft['scope'] })}><option>INSTANCE</option><option>TENANT</option><option disabled={!settings.namespace}>NAMESPACE</option></select></label>
              <label>Package<input required value={ruleDraft.selector.package} onChange={(event) => setRuleDraft({ ...ruleDraft, selector: { ...ruleDraft.selector, package: event.target.value } })} placeholder="vendor.package or *" /></label>
              <label>Version range<input required value={ruleDraft.selector.versionRange} onChange={(event) => setRuleDraft({ ...ruleDraft, selector: { ...ruleDraft.selector, versionRange: event.target.value } })} placeholder=">=1.2.0,&lt;2.0.0" /></label>
              <label>Stage<select value={ruleDraft.stages[0]} onChange={(event) => setRuleDraft({ ...ruleDraft, stages: [event.target.value as PluginPolicyStage] })}>{POLICY_STAGES.map((stage) => <option key={stage}>{stage}</option>)}</select></label>
              <label>Reason<input required value={ruleDraft.reason} onChange={(event) => setRuleDraft({ ...ruleDraft, reason: event.target.value })} /></label>
              <button className="button button-primary" type="submit" disabled={createRule.isPending}>Save rule</button>
            </form>
            <form onSubmit={(event: FormEvent) => { event.preventDefault(); previewQuarantine.mutate({ ...quarantineDraft, namespace: quarantineDraft.scope === 'NAMESPACE' ? settings.namespace : null }) }}>
              <h3>Emergency version disable</h3>
              <label>Scope<select value={quarantineDraft.scope} onChange={(event) => { setImpact(null); setQuarantineDraft({ ...quarantineDraft, scope: event.target.value as PluginQuarantineDraft['scope'] }) }}><option>INSTANCE</option><option>TENANT</option><option disabled={!settings.namespace}>NAMESPACE</option></select></label>
              <label>Package<input required value={quarantineDraft.package} onChange={(event) => { setImpact(null); setQuarantineDraft({ ...quarantineDraft, package: event.target.value }) }} placeholder="vendor.package" /></label>
              <label>Exact version<input required value={quarantineDraft.version} onChange={(event) => { setImpact(null); setQuarantineDraft({ ...quarantineDraft, version: event.target.value }) }} placeholder="1.2.3" /></label>
              <label>Reason<input required value={quarantineDraft.reason} onChange={(event) => setQuarantineDraft({ ...quarantineDraft, reason: event.target.value })} /></label>
              <button className="button button-secondary" type="submit" disabled={previewQuarantine.isPending}>Preview impact</button>
              {impact ? <div className="quarantine-impact"><strong>{impact.affectedFlows.length} flow revisions</strong><span>{impact.runningExecutions.length} running executions</span><button className="button button-danger" type="button" onClick={() => createQuarantine.mutate({ ...quarantineDraft, namespace: quarantineDraft.scope === 'NAMESPACE' ? settings.namespace : null })} disabled={createQuarantine.isPending}>Confirm disable</button></div> : null}
            </form>
          </div>
        ) : <p className="muted-copy">Policy changes require administration permission.</p>}
        {notice ? <p className="resource-notice" role="status">{notice}</p> : null}
        {createRule.error || deleteRule.error || previewQuarantine.error || createQuarantine.error ? <p className="resource-failure" role="alert">{(createRule.error || deleteRule.error || previewQuarantine.error || createQuarantine.error)?.message}</p> : null}
      </section>

      <section className="developer-portal" aria-labelledby="developer-portal-heading">
        <div className="section-heading">
          <div><p className="eyebrow">BUILD / VERIFY / PUBLISH</p><h2 id="developer-portal-heading">Plugin developer portal</h2></div>
          <Code2 size={22} aria-hidden="true" />
        </div>
        <p>Start with a uv-managed template, test configuration in the local sandbox, then reproduce every quality check with one command.</p>
        <div className="quality-levels" aria-label="Plugin quality levels">
          <article><PackageCheck size={18} aria-hidden="true" /><h3>Community</h3><p>Valid manifest, schemas and repository license.</p></article>
          <article><FlaskConical size={18} aria-hidden="true" /><h3>Verified</h3><p>All six checks pass with resilience, restart and redaction fixture evidence.</p></article>
          <article><BadgeCheck size={18} aria-hidden="true" /><h3>Certified</h3><p>Verified results reproduce from an immutable commit and public HTTPS CI run.</p></article>
        </div>
        <pre className="developer-command"><code>{`uv run amesh plugins scaffold ./my-plugin --name example.my-plugin
uv run amesh plugins sandbox ./my-plugin task.echo --configuration sample.yaml
uv run amesh plugins certify ./my-plugin --output certification-report.json`}</code></pre>
      </section>

      {registry.isPending ? <LoadingState label="Loading plugin registry" /> : null}
      {registry.error ? <ErrorState message={registry.error.message} retry={() => void registry.refetch()} /> : null}
      {!registry.isPending && !registry.error && !packages.length ? <EmptyState title="Registry is empty" body="Publish a signed plugin release through the registry API to see its supply-chain evidence here." /> : null}

      {!registry.isPending && !registry.error && packages.length ? (
        <section className="registry-grid" aria-label="Published plugin releases">
          {packages.map((release) => (
            <article className={`registry-card${release.yanked ? ' registry-card-yanked' : ''}`} key={`${release.name || 'legacy'}:${release.version || release.contentDigest}`}>
              <header>
                <div><p className="eyebrow">{release.manifest?.vendor || 'Unknown publisher'}</p><h2>{release.name || 'Legacy package'}</h2><code>{release.version || 'unversioned'}</code></div>
                <StatusBadge state={release.yanked ? 'PAUSED' : release.signals.security === 'current' ? 'PASS' : release.signals.security === 'critical' ? 'FAIL' : 'WARN'} />
              </header>
              <p>{release.manifest?.description || 'No publisher description.'}</p>
              <dl className="registry-facts">
                <div><dt>License</dt><dd>{release.metadata?.license || release.manifest?.license || 'Unknown'}</dd></div>
                <div><dt>Platform</dt><dd>{release.metadata?.supportedPlatformRange || 'Not declared'}</dd></div>
                <div><dt>SDK</dt><dd>{release.metadata?.sdkRange || 'Not declared'}</dd></div>
                <div><dt>Downloads</dt><dd><Download size={14} aria-hidden="true" />{release.signals.downloads}</dd></div>
                <div><dt>Certification</dt><dd>{release.signals.certification}</dd></div>
                <div><dt>Maintained</dt><dd>{release.signals.lastMaintainedAt ? formatDate(release.signals.lastMaintainedAt, settings.locale, settings.timezone) : 'Unknown'}</dd></div>
              </dl>
              <div className="registry-evidence" aria-label="Supply-chain attachments">
                {release.attachments.map((attachment) => <span key={attachment.kind}><FileCheck2 size={14} aria-hidden="true" />{attachment.kind.replace('-', ' ')}</span>)}
              </div>
              <footer>
                <span title={release.contentDigest}>{release.contentDigest.slice(0, 20)}…</span>
                <span>{release.metadataSignature ? `signed by ${release.metadataSignature.keyId}` : 'unsigned'}</span>
              </footer>
              {release.yanked ? <p className="registry-yank"><Ban size={15} aria-hidden="true" />{release.yankReason || 'This release is yanked.'}</p> : null}
            </article>
          ))}
        </section>
      ) : null}
    </div>
  )
}
