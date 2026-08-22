export type Capability =
  | 'flows.view'
  | 'flows.create'
  | 'executions.view'
  | 'executions.execute'
  | 'triggers.view'
  | 'triggers.manage'
  | 'checks.view'
  | 'checks.manage'
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
  outputs: Record<string, unknown>
  trigger: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface FlowInputSchemaProperty {
  type?: string | string[]
  enum?: unknown[]
  title?: string
  description?: string
  default?: unknown
  examples?: unknown[]
  writeOnly?: boolean
  ['x-amesh-input']?: {
    type: string
    sensitive: boolean
    placeholder: string | null
    prefill: unknown
    maxBytes: number | null
  }
}

export interface FlowDataContract {
  namespace: string
  flowId: string
  revision: number
  inputSchema: {
    properties: Record<string, FlowInputSchemaProperty>
    required: string[]
    additionalProperties: boolean
  }
  outputs: Record<string, unknown>
  variables: Record<string, unknown>
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

export type TriggerOccurrenceState =
  | 'ACCEPTED'
  | 'DEFERRED'
  | 'PROCESSING'
  | 'RETRY_WAIT'
  | 'SUCCEEDED'
  | 'DEAD_LETTERED'

export interface TriggerRuntimeState {
  trigger_definition_id: string
  tenant_id: string
  namespace: string
  flow_id: string
  flow_revision: number
  trigger_id: string
  trigger_type: string
  active: boolean
  paused: boolean
  checkpoint: Record<string, unknown>
  cursor: string | null
  last_evaluated_at: string | null
  next_evaluation_at: string | null
  last_occurrence_at: string | null
  last_success_at: string | null
  lag_seconds: number
  pending_count: number
  dead_letter_count: number
  consecutive_failures: number
  last_error: string | null
  last_decision: string
  updated_at: string
}

export interface TriggerOccurrence {
  occurrence_id: string
  tenant_id: string
  trigger_definition_id: string
  namespace: string
  flow_id: string
  flow_revision: number
  trigger_id: string
  trigger_type: string
  occurrence_key: string
  state: TriggerOccurrenceState
  attempt: number
  max_attempts: number
  available_at: string
  payload: Record<string, unknown>
  metadata: Record<string, unknown>
  evidence: Record<string, unknown>
  execution_id: string | null
  replay_of: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
}

export type CheckOutcome = 'PASS' | 'WARN' | 'FAIL' | 'ERROR'

export interface CheckEvaluation {
  evaluation_id: string
  tenant_id: string
  check_definition_id: string
  execution_id: string | null
  namespace: string
  flow_id: string
  flow_revision: number
  check_id: string
  check_type: 'DURATION' | 'START_DELAY' | 'FRESHNESS' | 'COMPLETION_WINDOW' | 'OUTPUT' | 'EXPRESSION'
  source: 'EXPLICIT' | 'NAMESPACE' | 'PLUGIN_DEFAULT'
  evaluation_point: 'STARTED' | 'TERMINAL' | 'DEADLINE' | 'FRESHNESS'
  subject_key: string
  outcome: CheckOutcome
  severity: 'WARN' | 'FAIL'
  reason: string
  evidence: Record<string, unknown>
  labels: Record<string, string>
  evaluated_at: string
}

export interface CheckComplianceSummary {
  group_key: string
  total: number
  passed: number
  warned: number
  failed: number
  errors: number
  compliance_rate: number
}

export interface NamespaceCheckPolicy {
  policy_id: string
  tenant_id: string
  namespace: string
  policy_key: string
  source: 'NAMESPACE' | 'PLUGIN_DEFAULT'
  task_type: string | null
  definition: {
    id: string
    type: CheckEvaluation['check_type']
    severity: 'WARN' | 'FAIL'
    threshold?: string
    expression?: string
    enabled: boolean
    actions: unknown[]
  }
  enabled: boolean
  created_at: string
  updated_at: string
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
  lifecyclePhase: 'MAIN' | 'ERROR' | 'FINALLY' | 'AFTER_EXECUTION'
  handlerOwnerId: string | null
}

export interface FlowGraphEdge {
  source: string
  target: string
  kind: 'contains' | 'dependsOn' | 'handles'
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
