import { Activity, ArrowRight, Blocks, Clock3, Workflow } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import type { UiSession } from '../api/types'
import { formatDate, formatNumber } from '../app/format'
import { useExecutions, useFlows } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'

export function DashboardPage({ session }: { session: UiSession }) {
  const { t } = useTranslation()
  const { settings } = useAppSettings()
  const flows = useFlows(session.capabilities['flows.view'])
  const executions = useExecutions(session.capabilities['executions.view'])
  const error = flows.error || executions.error
  const pending = flows.isPending || executions.isPending
  const executionData = executions.data || []
  const running = executionData.filter((item) => item.state === 'RUNNING').length
  const failed = executionData.filter((item) => item.state === 'FAILED').length

  return (
    <div className="page-stack">
      <header className="page-heading dashboard-heading">
        <div><p className="eyebrow">OPERATE / OVERVIEW</p><h1>{t('dashboard')}</h1><p>Live posture for {settings.tenant}{settings.namespace ? ` / ${settings.namespace}` : ''}.</p></div>
        <span className="live-indicator"><i />Live refresh · 15s</span>
      </header>
      {error ? <ErrorState message={error.message} retry={() => { void flows.refetch(); void executions.refetch() }} /> : null}
      {pending && !error ? <LoadingState /> : null}
      {!pending && !error ? (
        <>
          <section className="metric-strip" aria-label="Workspace metrics">
            <article><span><Workflow size={18} aria-hidden="true" />Flows</span><strong>{formatNumber(flows.data?.length || 0, settings.locale)}</strong><small>active definitions</small></article>
            <article><span><Activity size={18} aria-hidden="true" />Running</span><strong>{formatNumber(running, settings.locale)}</strong><small>current executions</small></article>
            <article className={failed ? 'metric-alert' : ''}><span><Blocks size={18} aria-hidden="true" />Failed</span><strong>{formatNumber(failed, settings.locale)}</strong><small>in latest 200</small></article>
            <article><span><Clock3 size={18} aria-hidden="true" />Observed</span><strong>{formatNumber(executionData.length, settings.locale)}</strong><small>retained sample</small></article>
          </section>
          <div className="dashboard-grid">
            <section className="data-section">
              <div className="section-heading"><div><p className="eyebrow">RECENT ACTIVITY</p><h2>Latest executions</h2></div><Link to="/executions">View all <ArrowRight size={16} aria-hidden="true" /></Link></div>
              {executionData.length ? (
                <div className="activity-list">
                  {executionData.slice(0, 6).map((execution) => (
                    <Link key={execution.execution_id} to={`/executions/${execution.execution_id}`} className="activity-row">
                      <span className="activity-glyph" aria-hidden="true"><Workflow size={17} /></span>
                      <span><strong>{execution.flow_id}</strong><small>{execution.namespace}</small></span>
                      <StatusBadge state={execution.state} />
                      <time dateTime={execution.updated_at}>{formatDate(execution.updated_at, settings.locale, settings.timezone)}</time>
                    </Link>
                  ))}
                </div>
              ) : <p className="inline-empty">No executions yet — run a flow through the API or CLI.</p>}
            </section>
            <aside className="system-panel">
              <p className="eyebrow">SYSTEM FABRIC</p><h2>Control plane</h2>
              <div className="fabric-diagram" aria-label="Connected API, PostgreSQL and workers">
                <span>API <i className="online" /></span><b /><span>PG <i className="online" /></span><b /><span>RUN <i /></span>
              </div>
              <dl><div><dt>Tenant boundary</dt><dd>{settings.tenant}</dd></div><div><dt>Policy source</dt><dd>Server authoritative</dd></div><div><dt>Telemetry</dt><dd>{session.telemetryEnabled ? 'Opted in' : 'Off'}</dd></div><div><dt>Version</dt><dd>{session.serverVersion}</dd></div></dl>
            </aside>
          </div>
        </>
      ) : null}
    </div>
  )
}
