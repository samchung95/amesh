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
}

export interface ExecutionDetail {
  execution: PersistedExecution
  taskRuns: PersistedTaskRun[]
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
