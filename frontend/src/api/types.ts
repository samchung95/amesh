export type Capability =
  | 'flows.view'
  | 'flows.create'
  | 'executions.view'
  | 'executions.execute'
  | 'namespaces.view'
  | 'plugins.view'
  | 'administration.manage'

export interface UiSession {
  principalId: string
  principalType: string
  display: string
  tenantId: string
  namespace: string | null
  capabilities: Record<Capability, boolean>
  telemetryEnabled: boolean
  serverVersion: string
}

export interface PersistedFlow {
  resource_id: string
  tenant_id: string
  namespace: string
  flow_id: string
  revision: number
  semantic_hash: string
  etag: string
}

export type ExecutionState = 'RUNNING' | 'SUCCESS' | 'FAILED'

export interface PersistedExecution {
  execution_id: string
  tenant_id: string
  state: ExecutionState
  epoch: number
  version: number
  namespace: string
  flow_id: string
  inputs: Record<string, unknown>
  trigger: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface PersistedTaskRun {
  task_run_id: string
  execution_id: string
  task_id: string
  state: 'WAITING' | 'RUNNING' | 'RETRY_DELAY' | 'SUCCESS' | 'FAILED'
  current_attempt: number
  version: number
  retry_at: string | null
  result: Record<string, unknown> | null
  iteration_key: string | null
  evidence: {
    cache?: {
      decision: 'HIT' | 'MISS' | 'MISS_EXPIRED' | 'MISS_INVALIDATED' | 'MISS_CONCURRENT' | 'REFRESH' | 'BYPASS'
      reason: string
      keyHash: string
      sourceExecutionId: string | null
      sourceTaskRunId: string | null
      sourceAttempt: number | null
      expiresAt: string | null
    }
    [key: string]: unknown
  }
}

export interface ExecutionDetail {
  execution: PersistedExecution
  taskRuns: PersistedTaskRun[]
}

export type ExecutionEvidenceKind = 'STATE' | 'LOG' | 'METRIC' | 'OUTPUT' | 'ARTIFACT'

export interface ExecutionEvidenceEvent {
  cursor: number
  event_id: string
  execution_id: string
  task_run_id: string | null
  kind: ExecutionEvidenceKind
  event_type: string
  payload: Record<string, unknown>
  occurred_at: string
  ingested_at: string
}

export interface ExecutionEvidencePage {
  items: ExecutionEvidenceEvent[]
  nextCursor: string | null
}

export interface FlowGraphNode {
  taskId: string
  label: string
  taskType: string
  order: number
  depth: number
  parentId: string | null
  dependencies: string[]
  children: string[]
  mode: 'SEQUENTIAL' | 'PARALLEL' | 'DAG' | 'FOREACH' | 'WHILE' | 'UNTIL' | null
  failurePolicy: 'FAIL_FAST' | 'CONTINUE_ON_ERROR' | 'COLLECT_ALL'
  maxConcurrency: number | null
  state: string | null
  result: Record<string, unknown> | null
  iterationCount: number | null
}

export interface FlowGraphEdge {
  source: string
  target: string
  kind: 'contains' | 'dependsOn'
}

export interface FlowGraph {
  namespace: string
  flowId: string
  revision: number
  nodes: FlowGraphNode[]
  edges: FlowGraphEdge[]
}

export interface HealthResponse {
  status: string
  version: string
}

export interface AuthenticationProvider {
  id: string
  kind: string
  display_name: string
  interactive: boolean
}

export interface LoginResponse {
  principalId: string
  display: string
  idleExpiresAt: string
  absoluteExpiresAt: string
}
