import { ArrowLeft, Braces, Clock3, Workflow } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { compactId, formatDate } from '../app/format'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'

export function ExecutionDetailPage() {
  const { executionId = '' } = useParams()
  const api = useApiClient()
  const { settings } = useAppSettings()
  const detail = useQuery({ queryKey: ['execution', executionId, settings.tenant], queryFn: () => api.execution(executionId), enabled: Boolean(executionId) })
  if (detail.isPending) return <LoadingState label="Loading execution detail" />
  if (detail.error) return <ErrorState message={detail.error.message} retry={() => void detail.refetch()} />
  const { execution, taskRuns } = detail.data
  return (
    <div className="page-stack">
      <Link className="back-link" to="/executions"><ArrowLeft size={16} aria-hidden="true" />Executions</Link>
      <header className="page-heading detail-heading"><div><p className="eyebrow">EXECUTION / {compactId(execution.execution_id)}</p><h1>{execution.flow_id}</h1><p>{execution.namespace}</p></div><StatusBadge state={execution.state} /></header>
      <section className="detail-facts" aria-label="Execution facts"><div><Workflow size={17} aria-hidden="true" /><span><small>Flow</small><strong>{execution.flow_id}</strong></span></div><div><Clock3 size={17} aria-hidden="true" /><span><small>Created</small><strong>{formatDate(execution.created_at, settings.locale, settings.timezone)}</strong></span></div><div><Braces size={17} aria-hidden="true" /><span><small>Epoch / version</small><strong>{execution.epoch} / {execution.version}</strong></span></div></section>
      <section className="data-section"><div className="section-heading"><div><p className="eyebrow">TASK PLAN</p><h2>Task runs</h2></div><span>{taskRuns.length} tasks</span></div><div className="task-run-list">{taskRuns.map((task, index) => <article key={task.task_run_id}><span className="task-index">{String(index + 1).padStart(2, '0')}</span><div><strong>{task.task_id}</strong><small>{compactId(task.task_run_id)} · attempt {task.current_attempt}</small></div><StatusBadge state={task.state} /><details><summary>Result</summary><pre>{JSON.stringify(task.result, null, 2)}</pre></details></article>)}</div></section>
    </div>
  )
}
