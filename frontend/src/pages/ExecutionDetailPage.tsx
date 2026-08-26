import { ArrowLeft } from 'lucide-react'
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'

import type {
  AgentSessionEvent,
  BackfillSpec,
  ExecutionEvidenceEvent,
  ExecutionInterventionAction,
  ExecutionInterventionPreview,
  UiSession,
} from '../api/types'
import { compactId } from '../app/format'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import { AgentRunInspector } from '../components/AgentRunInspector'
import { ExecutionDebugger } from '../components/ExecutionDebugger'
import {
  LARGE_GRAPH_THRESHOLD,
  mergeEvidence,
  TASK_RUN_PAGE_SIZE,
} from '../components/executionDebugModel'
import { StatusBadge } from '../components/StatusBadge'

const terminalStates = new Set(['SUCCESS', 'FAILED', 'WARNING', 'CANCELLED'])

export function ExecutionDetailPage({ session }: { session: UiSession }) {
  const { executionId = '' } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const offset = Math.max(0, Number(searchParams.get('offset') || 0))
  const detail = useQuery({
    queryKey: ['execution', executionId, settings.tenant, offset],
    queryFn: () => api.execution(executionId, offset, TASK_RUN_PAGE_SIZE),
    enabled: Boolean(executionId),
    refetchInterval: 2_000,
  })
  const totalTasks = detail.data?.taskRunSummary?.total ?? detail.data?.taskRuns.length ?? 0
  const executionState = detail.data?.execution.state
  const graph = useQuery({
    queryKey: ['execution-graph', executionId, settings.tenant],
    queryFn: () => api.executionGraph(executionId),
    enabled: Boolean(executionId) && detail.isSuccess && totalTasks <= LARGE_GRAPH_THRESHOLD,
    refetchInterval: 2_000,
  })
  const initialEvidence = useQuery({
    queryKey: ['execution-evidence-initial', executionId, settings.tenant],
    queryFn: () => api.executionEvidence(executionId),
    enabled: Boolean(executionId),
    staleTime: Number.POSITIVE_INFINITY,
  })
  const artifacts = useQuery({ queryKey: ['execution-files', executionId, settings.tenant], queryFn: () => api.executionFiles(executionId), enabled: Boolean(executionId), refetchInterval: 5_000 })
  const subflows = useQuery({ queryKey: ['execution-subflows', executionId, settings.tenant], queryFn: () => api.executionSubflows(executionId), enabled: Boolean(executionId), refetchInterval: 5_000 })
  const parent = useQuery({ queryKey: ['execution-parent', executionId, settings.tenant], queryFn: () => api.executionParentSubflow(executionId), enabled: Boolean(executionId), staleTime: 10_000 })
  const interventions = useQuery({ queryKey: ['execution-interventions', executionId, settings.tenant], queryFn: () => api.executionInterventions(executionId), enabled: Boolean(executionId), refetchInterval: 5_000 })
  const agentSessions = useQuery({
    queryKey: ['execution-agent-sessions', executionId, settings.tenant],
    queryFn: () => api.executionAgentSessions(executionId),
    enabled: Boolean(executionId),
    refetchInterval: terminalStates.has(executionState ?? '') ? false : 2_000,
  })
  const requestedAgentSession = searchParams.get('agentSession')
  const selectedAgentSession = agentSessions.data?.find((item) => item.sessionId === requestedAgentSession)
    ?? agentSessions.data?.[0]
  const agentSessionDetail = useInfiniteQuery({
    queryKey: ['execution-agent-session-detail', executionId, selectedAgentSession?.taskRunId, selectedAgentSession?.attempt, settings.tenant],
    queryFn: ({ pageParam }) => api.executionAgentSessionDetail(
      executionId,
      selectedAgentSession!.taskRunId,
      selectedAgentSession!.attempt,
      pageParam,
      100,
    ),
    initialPageParam: 0,
    getNextPageParam: (page) => page.nextEventIndex ?? undefined,
    enabled: Boolean(executionId && selectedAgentSession),
    refetchInterval: terminalStates.has(executionState ?? '') ? false : 2_000,
  })
  const humanTasks = useQuery({
    queryKey: ['execution-human-tasks', executionId, settings.tenant],
    queryFn: () => api.humanTasks(detail.data!.execution.namespace, true),
    enabled: detail.isSuccess && session.capabilities['humanTasks.view'],
    refetchInterval: 5_000,
  })
  const [streamedEvidence, setStreamedEvidence] = useState<ExecutionEvidenceEvent[]>([])
  const [streamState, setStreamState] = useState<'connecting' | 'live' | 'reconnecting' | 'complete'>('connecting')
  const seededCursor = useRef<{ executionId: string; cursor: string | null } | null>(null)
  const evidence = mergeEvidence(initialEvidence.data?.items ?? [], streamedEvidence)
  const agentEvents = [...new Map(
    (agentSessionDetail.data?.pages.flatMap((page) => page.events) ?? [])
      .map((event) => [event.eventIndex, event] as const),
  ).values()].sort((left: AgentSessionEvent, right: AgentSessionEvent) => left.eventIndex - right.eventIndex)

  useEffect(() => {
    if (!initialEvidence.data || !executionState) return
    const controller = new AbortController()
    let cursor = seededCursor.current?.executionId === executionId
      ? seededCursor.current.cursor
      : initialEvidence.data.nextCursor
    let retrying = false
    let pending: ExecutionEvidenceEvent[] = []
    let flushTimer: number | null = null
    const flush = () => {
      if (pending.length) {
        const batch = pending
        pending = []
        setStreamedEvidence((current) => mergeEvidence(current, batch))
      }
      flushTimer = null
    }
    const receive = (event: ExecutionEvidenceEvent & { nextCursor: string }) => {
      cursor = event.nextCursor
      seededCursor.current = { executionId, cursor: event.nextCursor }
      pending.push(event)
      setStreamState('live')
      if (flushTimer === null) flushTimer = window.setTimeout(flush, 40)
    }
    const run = async () => {
      while (!controller.signal.aborted) {
        try {
          setStreamState(retrying ? 'reconnecting' : 'connecting')
          await api.streamExecutionEvidence(executionId, cursor, receive, controller.signal)
          flush()
          if (terminalStates.has(executionState)) {
            setStreamState('complete')
            break
          }
          retrying = true
        } catch {
          if (controller.signal.aborted) break
          retrying = true
          setStreamState('reconnecting')
          await new Promise((resolve) => window.setTimeout(resolve, 1_000))
        }
      }
    }
    void run()
    return () => {
      controller.abort()
      if (flushTimer !== null) window.clearTimeout(flushTimer)
    }
  }, [api, executionId, executionState, initialEvidence.data])

  const refreshExecution = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['execution', executionId] }),
      queryClient.invalidateQueries({ queryKey: ['execution-graph', executionId] }),
      queryClient.invalidateQueries({ queryKey: ['execution-interventions', executionId] }),
    ])
  }
  const interventionMutation = useMutation({
    mutationFn: ({ preview, reason }: { preview: ExecutionInterventionPreview; reason: string }) => api.applyExecutionIntervention(executionId, preview, reason),
    onSuccess: refreshExecution,
  })
  const backfillMutation = useMutation({ mutationFn: (spec: BackfillSpec) => api.createBackfill(spec) })

  if (detail.isPending) return <LoadingState label="Loading execution detail" />
  if (detail.error) return <ErrorState message={detail.error.message} retry={() => void detail.refetch()} />
  const { execution } = detail.data
  return (
    <div className="page-stack">
      <Link className="back-link" to="/executions"><ArrowLeft size={16} aria-hidden="true" />Executions</Link>
      <header className="page-heading detail-heading">
        <div><p className="eyebrow">EXECUTION / {compactId(execution.execution_id)}</p><h1>{execution.flow_id}</h1><p>{execution.namespace}</p></div>
        <StatusBadge state={execution.state} />
      </header>
      {initialEvidence.error ? <p className="form-error" role="alert">Evidence stream unavailable: {initialEvidence.error.message}</p> : null}
      {(agentSessions.error || selectedAgentSession) ? <section className="agent-run-inspector-shell" aria-label="Agent execution evidence">
        {selectedAgentSession && (agentSessions.data?.length ?? 0) > 1 ? <div className="agent-run-inspector-toolbar">
          <label><span>Agent session</span><select value={selectedAgentSession.sessionId} onChange={(event) => {
            const next = new URLSearchParams(searchParams)
            next.set('agentSession', event.target.value)
            setSearchParams(next)
          }}>{agentSessions.data?.map((item) => <option key={item.sessionId} value={item.sessionId}>{compactId(item.taskRunId)} · attempt {item.attempt}</option>)}</select></label>
          <span>{agentEvents.length} canonical events loaded</span>
        </div> : null}
        <AgentRunInspector
          session={agentSessionDetail.data?.pages.at(-1)?.session ?? selectedAgentSession}
          executionState={execution.state}
          events={agentEvents}
          pending={Boolean(selectedAgentSession) && agentSessionDetail.isPending}
          error={agentSessions.error?.message ?? agentSessionDetail.error?.message ?? null}
          locale={settings.locale}
          timezone={settings.timezone}
        />
        {agentSessionDetail.hasNextPage ? <button className="button button-secondary agent-run-load-more" type="button" disabled={agentSessionDetail.isFetchingNextPage} onClick={() => void agentSessionDetail.fetchNextPage()}>{agentSessionDetail.isFetchingNextPage ? 'Loading events…' : 'Load next 100 events'}</button> : null}
      </section> : null}
      <ExecutionDebugger
        detail={detail.data}
        graph={graph.data}
        graphLoading={graph.isPending && graph.fetchStatus !== 'idle'}
        evidence={evidence}
        streamState={streamState}
        artifacts={artifacts.data ?? []}
        subflows={subflows.data ?? []}
        parent={parent.data ?? null}
        interventions={interventions.data ?? []}
        humanTasks={(humanTasks.data ?? []).filter((task) => task.executionId === executionId)}
        locale={settings.locale}
        timezone={settings.timezone}
        canManage={session.capabilities['executions.manage']}
        canExecute={session.capabilities['executions.execute']}
        busy={interventionMutation.isPending || backfillMutation.isPending}
        onPreviewIntervention={(action: ExecutionInterventionAction, checkpoint?: string) => api.previewExecutionIntervention(executionId, action, checkpoint)}
        onApplyIntervention={async (preview, reason) => { await interventionMutation.mutateAsync({ preview, reason }) }}
        onPreviewBackfill={(spec) => api.previewBackfill(spec)}
        onCreateBackfill={(spec) => backfillMutation.mutateAsync(spec)}
        onDownloadArtifact={async (artifact) => {
          const blob = await api.downloadExecutionFile(executionId, artifact.artifact_id)
          const url = URL.createObjectURL(blob)
          const anchor = document.createElement('a')
          anchor.href = url
          anchor.download = artifact.logical_path?.split('/').at(-1) || 'execution-artifact'
          anchor.click()
          URL.revokeObjectURL(url)
        }}
      />
    </div>
  )
}
