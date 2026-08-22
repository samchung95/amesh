import { Ban, Download, FileCheck2, PackageCheck, RefreshCw, ShieldCheck } from 'lucide-react'

import { formatDate } from '../app/format'
import { usePluginRegistry } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'

export function PluginsPage() {
  const registry = usePluginRegistry()
  const { settings } = useAppSettings()
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
