import { ArrowLeft, Workflow } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import { FlowGraphView } from '../components/FlowGraphView'

export function FlowDetailPage() {
  const { namespace = '', flowId = '' } = useParams()
  const api = useApiClient()
  const { settings } = useAppSettings()
  const graph = useQuery({
    queryKey: ['flow-graph', namespace, flowId, settings.tenant],
    queryFn: () => api.flowGraph(namespace, flowId),
    enabled: Boolean(namespace && flowId),
  })

  if (graph.isPending) return <LoadingState label="Loading workflow graph" />
  if (graph.error) return <ErrorState message={graph.error.message} retry={() => void graph.refetch()} />

  return (
    <div className="page-stack">
      <Link className="back-link" to="/flows"><ArrowLeft size={16} aria-hidden="true" />Flows</Link>
      <header className="page-heading detail-heading">
        <div><p className="eyebrow">FLOW / REVISION {graph.data.revision}</p><h1>{graph.data.flowId}</h1><p>{graph.data.namespace}</p></div>
        <span className="live-indicator"><Workflow size={15} aria-hidden="true" />Definition</span>
      </header>
      <FlowGraphView graph={graph.data} />
    </div>
  )
}
