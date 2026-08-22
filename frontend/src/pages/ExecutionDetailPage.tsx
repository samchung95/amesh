import { ArrowLeft, Braces, Clock3, Workflow } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { compactId, formatDate } from '../app/format'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import { FlowGraphView } from '../components/FlowGraphView'
import { ExecutionEvidenceTimeline } from '../components/ExecutionEvidenceTimeline'
import { StatusBadge } from '../components/StatusBadge'

export function ExecutionDetailPage() {
  const { executionId = '' } = useParams()
  const api = useApiClient()
  const { settings } = useAppSettings()
  const detail = useQuery({ queryKey: ['execution', executionId, settings.tenant], queryFn: () => api.execution(executionId), enabled: Boolean(executionId), refetchInterval: 2_000 })
  const graph = useQuery({ queryKey: ['execution-graph', executionId, settings.tenant], queryFn: () => api.executionGraph(executionId), enabled: Boolean(executionId), refetchInterval: 2_000 })
  const evidence = useQuery({ queryKey: ['execution-evidence', executionId, settings.tenant], queryFn: () => api.executionEvidence(executionId), enabled: Boolean(executionId), refetchInterval: 1_000 })
  if (detail.isPending) return <LoadingState label="Loading execution detail" />
  if (detail.error) return <ErrorState message={detail.error.message} retry={() => void detail.refetch()} />
  const { execution, taskRuns } = detail.data
  return (
    <div className="page-stack">
      <Link className="back-link" to="/executions"><ArrowLeft size={16} aria-hidden="true" />Executions</Link>
      <header className="page-heading detail-heading"><div><p className="eyebrow">EXECUTION / {compactId(execution.execution_id)}</p><h1>{execution.flow_id}</h1><p>{execution.namespace}</p></div><StatusBadge state={execution.state} /></header>
      <section className="detail-facts" aria-label="Execution facts"><div><Workflow size={17} aria-hidden="true" /><span><small>Flow</small><strong>{execution.flow_id}</strong></span></div><div><Clock3 size={17} aria-hidden="true" /><span><small>Created</small><strong>{formatDate(execution.created_at, settings.locale, settings.timezone)}</strong></span></div><div><Braces size={17} aria-hidden="true" /><span><small>Epoch / version</small><strong>{execution.epoch} / {execution.version}</strong></span></div></section>
      {graph.isPending ? <LoadingState label="Loading live workflow graph" /> : null}
      {graph.error ? <ErrorState message={graph.error.message} retry={() => void graph.refetch()} /> : null}
      {graph.data ? <FlowGraphView graph={graph.data} /> : null}
      {evidence.isPending ? <LoadingState label="Loading durable execution evidence" /> : null}
      {evidence.error ? <ErrorState message={evidence.error.message} retry={() => void evidence.refetch()} /> : null}
      {evidence.data ? <ExecutionEvidenceTimeline events={evidence.data.items} locale={settings.locale} timezone={settings.timezone} /> : null}
      <section className="data-section"><div className="section-heading"><div><p className="eyebrow">TASK PLAN</p><h2>Task runs</h2></div><span>{taskRuns.length} tasks</span></div><div className="task-run-list">{taskRuns.map((task, index) => {
        const cache = task.evidence?.cache
        return <article key={task.task_run_id}><span className="task-index">{String(index + 1).padStart(2, '0')}</span><div><strong>{task.task_id}</strong><small>{compactId(task.task_run_id)} · attempt {task.current_attempt}</small>{cache ? <small className={`cache-decision cache-${cache.decision.toLowerCase()}`} title={cache.reason}>Cache {cache.decision.replaceAll('_', ' ').toLowerCase()} · {cache.reason}</small> : null}</div><StatusBadge state={task.state} /><details><summary>Result</summary><pre>{JSON.stringify(task.result, null, 2)}</pre>{cache ? <><h4 className="cache-summary">Cache provenance</h4><pre>{JSON.stringify(cache, null, 2)}</pre></> : null}</details></article>
      })}</div></section>
    </div>
  )
}
