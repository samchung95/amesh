import { Activity, CircleCheck, RefreshCw, Search, ShieldCheck, TriangleAlert } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import type { CheckOutcome, UiSession } from '../../api/types'
import { compactId, formatDate } from '../../app/format'
import { useCheckCompliance, useCheckEvaluations, useCheckPolicies } from '../../app/queries'
import { useAppSettings } from '../../app/settings'
import { EmptyState, ErrorState, LoadingState, StatusBadge } from '../../shared/ui'

const outcomes: CheckOutcome[] = ['PASS', 'WARN', 'FAIL', 'ERROR']

export function ChecksPage({ session }: { session: UiSession }) {
  const { settings } = useAppSettings()
  const evaluations = useCheckEvaluations(session.capabilities['checks.view'])
  const compliance = useCheckCompliance(session.capabilities['checks.view'])
  const policies = useCheckPolicies(session.capabilities['checks.view'])
  const [query, setQuery] = useState('')
  const [outcome, setOutcome] = useState<CheckOutcome | ''>('')

  const refresh = async () => {
    await Promise.all([evaluations.refetch(), compliance.refetch(), policies.refetch()])
  }
  const rows = useMemo(
    () =>
      (evaluations.data || []).filter((item) => {
        const haystack = `${item.namespace}.${item.flow_id} ${item.check_id} ${item.check_type} ${item.reason}`.toLowerCase()
        return (!outcome || item.outcome === outcome) && haystack.includes(query.toLowerCase())
      }),
    [evaluations.data, outcome, query],
  )
  const totals = (evaluations.data || []).reduce(
    (current, item) => ({ ...current, [item.outcome]: current[item.outcome] + 1 }),
    { PASS: 0, WARN: 0, FAIL: 0, ERROR: 0 } as Record<CheckOutcome, number>,
  )
  const total = outcomes.reduce((sum, item) => sum + totals[item], 0)
  const complianceRate = total ? Math.round((totals.PASS / total) * 100) : 0
  const pending = evaluations.isPending || compliance.isPending || policies.isPending
  const error = evaluations.error || compliance.error || policies.error

  return (
    <div className="page-stack">
      <header className="page-heading">
        <div>
          <p className="eyebrow">OPERATE / POLICY EVIDENCE</p>
          <h1>Execution checks</h1>
          <p>Duration, start delay, freshness, completion, output and expression compliance.</p>
        </div>
        <button className="button button-secondary" type="button" onClick={() => void refresh()} disabled={evaluations.isFetching || compliance.isFetching}>
          <RefreshCw className={evaluations.isFetching || compliance.isFetching ? 'spin' : ''} size={17} aria-hidden="true" />
          Refresh
        </button>
      </header>

      <section className="metric-strip" aria-label="Check summary">
        <article><span><ShieldCheck size={16} aria-hidden="true" />Compliance</span><strong>{complianceRate}%</strong><small>{total} recent evaluations</small></article>
        <article><span><CircleCheck size={16} aria-hidden="true" />Passing</span><strong>{totals.PASS}</strong><small>policy conditions satisfied</small></article>
        <article className={totals.WARN ? 'metric-alert' : ''}><span><TriangleAlert size={16} aria-hidden="true" />Warnings</span><strong>{totals.WARN}</strong><small>attention without execution failure</small></article>
        <article className={totals.FAIL + totals.ERROR ? 'metric-alert' : ''}><span><Activity size={16} aria-hidden="true" />Fail / error</span><strong>{totals.FAIL + totals.ERROR}</strong><small>{totals.FAIL} failed · {totals.ERROR} evaluation errors</small></article>
      </section>

      {pending ? <LoadingState label="Loading execution checks" /> : null}
      {error ? <ErrorState message={error.message} retry={() => void refresh()} /> : null}

      {!compliance.isPending && !compliance.error ? (
        <section className="data-section" aria-labelledby="compliance-heading">
          <div className="section-heading"><div><p className="eyebrow">FLOW COMPLIANCE</p><h2 id="compliance-heading">Current aggregation</h2></div><span className="live-indicator"><i className="online" />10s refresh</span></div>
          {!compliance.data?.length ? <EmptyState title="No compliance evidence" body="Run a flow revision that declares checks or selects a namespace policy." /> : null}
          {compliance.data?.length ? (
            <div className="table-shell"><table><thead><tr><th>Flow</th><th>Compliance</th><th>Pass</th><th>Warn</th><th>Fail</th><th>Error</th></tr></thead><tbody>
              {compliance.data.map((item) => <tr key={item.group_key}><td><strong>{item.group_key}</strong></td><td><strong>{Math.round(item.compliance_rate * 100)}%</strong><small className="cell-subtitle">{item.total} evaluations</small></td><td>{item.passed}</td><td>{item.warned}</td><td>{item.failed}</td><td>{item.errors}</td></tr>)}
            </tbody></table></div>
          ) : null}
        </section>
      ) : null}

      {!evaluations.isPending && !evaluations.error ? (
        <section className="data-section" aria-labelledby="evaluation-heading">
          <div className="section-heading"><div><p className="eyebrow">DURABLE LEDGER</p><h2 id="evaluation-heading">Recent evaluations</h2></div></div>
          <div className="toolbar trigger-toolbar" aria-label="Check filters">
            <label className="search-field"><Search size={17} aria-hidden="true" /><span className="sr-only">Search checks</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search flow, check or reason" /></label>
            <label className="filter-select"><span>Outcome</span><select value={outcome} onChange={(event) => setOutcome(event.target.value as CheckOutcome | '')}><option value="">All outcomes</option>{outcomes.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
            <span className="result-count">{rows.length} / {evaluations.data?.length || 0} evaluations</span>
          </div>
          {!rows.length ? <EmptyState title="No evaluations match" body="Clear the filters or run a checked flow." /> : null}
          {rows.length ? (
            <div className="table-shell trigger-table"><table><thead><tr><th>Check</th><th>Flow / revision</th><th>Outcome</th><th>Point</th><th>Evidence</th><th>Evaluated</th><th>Execution</th></tr></thead><tbody>
              {rows.map((item) => (
                <tr key={item.evaluation_id}>
                  <td><strong>{item.check_id}</strong><small className="cell-subtitle"><code>{item.check_type}</code> · {item.source}</small></td>
                  <td>{item.namespace}.{item.flow_id}<small className="cell-subtitle">revision {item.flow_revision}</small></td>
                  <td><StatusBadge state={item.outcome} /></td>
                  <td><code>{item.evaluation_point}</code></td>
                  <td className="trigger-decision"><span>{item.reason}</span><small>{item.severity} policy</small></td>
                  <td><time dateTime={item.evaluated_at}>{formatDate(item.evaluated_at, settings.locale, settings.timezone)}</time></td>
                  <td>{item.execution_id ? <Link className="button button-compact button-secondary" to={`/executions/${item.execution_id}`}>{compactId(item.execution_id)}</Link> : <span className="hash">flow scope</span>}</td>
                </tr>
              ))}
            </tbody></table></div>
          ) : null}
        </section>
      ) : null}

      {!policies.isPending && !policies.error ? (
        <section className="data-section" aria-labelledby="policy-heading">
          <div className="section-heading"><div><p className="eyebrow">REUSABLE POLICY</p><h2 id="policy-heading">Namespace and plugin defaults</h2></div><span className="result-count">{policies.data?.length || 0} policies</span></div>
          {!policies.data?.length ? <EmptyState title="No reusable policies" body="Checks declared directly on flows are still evaluated. Use the policy API to share baselines." /> : null}
          {policies.data?.length ? (
            <div className="table-shell"><table><thead><tr><th>Policy</th><th>Namespace</th><th>Source</th><th>Check</th><th>Target</th><th>State</th></tr></thead><tbody>
              {policies.data.map((item) => <tr key={item.policy_id}><td><strong>{item.policy_key}</strong></td><td>{item.namespace}</td><td><code>{item.source}</code></td><td>{item.definition.id}<small className="cell-subtitle">{item.definition.type}</small></td><td>{item.task_type || 'selected flows'}</td><td><StatusBadge state={item.enabled ? 'RUNNING' : 'PAUSED'} /></td></tr>)}
            </tbody></table></div>
          ) : null}
        </section>
      ) : null}
    </div>
  )
}
