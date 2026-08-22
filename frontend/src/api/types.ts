export type Capability =
  | 'flows.view'
  | 'flows.create'
  | 'flows.update'
  | 'executions.view'
  | 'executions.execute'
  | 'executions.manage'
  | 'triggers.view'
  | 'triggers.manage'
  | 'checks.view'
  | 'checks.manage'
  | 'namespaces.view'
  | 'namespaceResources.read'
  | 'namespaceResources.write'
  | 'secretBindings.write'
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
  lifecycle?: 'DRAFT' | 'ACTIVE' | 'DISABLED' | 'ARCHIVED'
  metadata: {
    labels: Record<string, string>
  }
}

export interface SourcePosition {
  line: number
  column: number
  offset: number
}

export interface FlowValidationIssue {
  code: string
  message: string
  path: string
  hint: string
  sourceRange: { start: SourcePosition; end: SourcePosition } | null
  severity: string
}

export interface FlowValidationResult {
  valid: boolean
  irVersion: 'amesh.flow/v1' | null
  semantic_hash: string | null
  canonical: Record<string, unknown> | null
  issues: FlowValidationIssue[]
}

export interface JsonSchema {
  type?: string | string[]
  title?: string
  description?: string
  default?: unknown
  enum?: unknown[]
  properties?: Record<string, JsonSchema>
  required?: string[]
  items?: JsonSchema
  $defs?: Record<string, JsonSchema>
  [key: string]: unknown
}

export interface FlowResourceSchema {
  type: string
  kind: 'task' | 'trigger' | 'input'
  configurationSchema: JsonSchema
  editor: {
    title: string
    description: string
    category: string
    propertyOrder: string[]
  }
}

export interface FlowEditorSchema {
  schemaVersion: 'amesh.flow-editor/v1'
  flowSchema: JsonSchema
  resourceCatalog: {
    schemaVersion: 'amesh.resource-catalog/v1'
    resources: FlowResourceSchema[]
  }
  expressionContext: Record<string, string>
}

export interface FlowDocumentExport {
  namespace: string
  flowId: string
  revision: number
  semanticHash: string
  document: Record<string, unknown>
}

export interface FlowRevisionRecord {
  resource_id: string
  tenant_id: string
  namespace: string
  flow_id: string
  revision: number
  semantic_hash: string
  source: string | null
  source_commit: string | null
  environment: string | null
  deployment: Record<string, unknown>
  created_by: string
  created_at: string
}

export interface FlowRevisionDiff {
  from_revision: number
  to_revision: number
  human: string
  operations: Array<Record<string, unknown>>
}

export interface FlowFormatResponse {
  document: string | null
  validation: FlowValidationResult
}

export interface ExpressionPreviewResponse {
  result: unknown
  redactedContext: Record<string, unknown>
  compatibilityVersion: string
}

export type ExecutionState =
  | 'CREATED'
  | 'QUEUED'
  | 'RUNNING'
  | 'PAUSED'
  | 'CANCELLING'
  | 'CANCELLED'
  | 'SUCCESS'
  | 'FAILED'
  | 'WARNING'
  | 'RESTARTING'

export interface PersistedExecution {
  execution_id: string
  tenant_id: string
  state: ExecutionState
  epoch: number
  version: number
  namespace: string
  flow_id: string
  flow_revision: number
  inputs: Record<string, unknown>
  outputs: Record<string, unknown>
  labels: Record<string, string>
  trigger: Record<string, unknown>
  created_by: string
  created_at: string
  updated_at: string
  timeout_at: string | null
  cancel_deadline_at: string | null
  lifecycle_evidence: Record<string, unknown>
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

export interface FlowMetadata {
  namespace: string
  flowId: string
  revision: number
  labels: Record<string, string>
  pluginResolution: {
    defaults?: {
      schemaVersion: number
      namespaceLineage: string[]
      tasks: Record<string, {
        type: string
        effective: Record<string, unknown>
        origins: Record<string, {
          source: 'namespace' | 'flow' | 'task'
          namespace: string | null
          taskPath: string
          forced: boolean
        }>
      }>
    }
  }
}

export interface PersistedTaskRun {
  task_run_id: string
  execution_id: string
  task_id: string
  state: 'WAITING' | 'RUNNING' | 'RETRY_DELAY' | 'SUCCESS' | 'FAILED' | 'CANCELLED'
  current_attempt: number
  version: number
  retry_at: string | null
  result: Record<string, unknown> | null
  iteration_key: string | null
  labels: Record<string, string>
  failure_category: string | null
  lifecycle_phase: 'MAIN' | 'ERROR' | 'FINALLY' | 'AFTER_EXECUTION'
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
  taskRunSummary: TaskRunSummary | null
  taskRunOffset: number
}

export interface TaskRunSummary {
  total: number
  waiting: number
  running: number
  retry_delay: number
  succeeded: number
  failed: number
  cancelled: number
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

export interface ExecutionEvidenceStreamEvent extends ExecutionEvidenceEvent {
  nextCursor: string
}

export type ExecutionInterventionAction = 'PAUSE' | 'RESUME' | 'REQUEST_CANCEL' | 'CONFIRM_CANCEL' | 'FORCE_CANCEL' | 'RESTART'

export interface ExecutionInterventionPreview {
  execution_id: string
  action: ExecutionInterventionAction
  current_state: ExecutionState
  predicted_state: ExecutionState
  current_version: number
  current_epoch: number
  checkpoint_task_id: string | null
  impacted_task_ids: string[]
  preserved_task_ids: string[]
  invalidates_active_claims: boolean
  destructive: boolean
  force_available_at: string | null
  consequences: string[]
}

export interface ExecutionInterventionRecord {
  sequence: number
  action: ExecutionInterventionAction
  event_type: string
  actor_id: string
  reason: string | null
  occurred_at: string
  payload: Record<string, unknown>
}

export interface PersistedSubflow {
  relationship_id: string
  parent_execution_id: string
  parent_task_run_id: string
  parent_attempt: number
  child_execution_id: string
  invocation_key: string
  mode: 'SYNC' | 'ASYNC' | 'DETACHED'
  depth: number
  target_revision: number
  parent_namespace: string
  parent_flow_id: string
  parent_flow_revision: number
  child_namespace: string
  child_flow_id: string
  child_state: ExecutionState
  created_by: string
  created_at: string
}

export interface ExecutionArtifact {
  artifact_id: string
  execution_id: string
  task_run_id: string
  attempt: number
  uri: string
  size_bytes: number
  media_type: string | null
  checksum_sha256: string | null
  logical_path: string | null
  lineage: string[]
  occurred_at: string
  ingested_at: string
}

export interface BackfillSpec {
  namespace: string
  flowId: string
  flowRevision: number
  selection: {
    sourceExecutionIds?: string[]
    timeRange?: { start: string; end: string; intervalSeconds: number }
  }
  inputs: Record<string, unknown>
  labels: Record<string, string>
  maxConcurrency: number
  ratePerMinute: number
  priority: number
}

export interface BackfillPreview {
  selectionKind: 'TIME_RANGE' | 'PARTITIONS' | 'OCCURRENCES' | 'REPLAY'
  executionCount: number
  estimatedTaskRuns: number
  estimatedCostUnits: number
  idempotencyKeyTemplate: string
  warnings: string[]
}

export interface BackfillRecord {
  backfillId: string
  state: 'RUNNING' | 'PAUSED' | 'CANCELLED' | 'COMPLETED'
  total: number
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

export interface NamespaceFile {
  namespace: string
  path: string
  version: number
  resourceVersion: number
  sizeBytes: number
  checksumSha256: string
  contentType: string | null
  metadata: Record<string, unknown>
  originNamespace: string
  inherited: boolean
  createdAt: string
  updatedAt: string
}

export interface NamespaceFileVersion {
  namespace: string
  path: string
  version: number
  sizeBytes: number
  checksumSha256: string
  contentType: string | null
  createdBy: string
  createdAt: string
}

export type KeyValueType = 'STRING' | 'NUMBER' | 'BOOLEAN' | 'DATETIME' | 'DATE' | 'DURATION' | 'JSON'

export interface KeyValueEntry {
  namespace: string
  key: string
  type: KeyValueType
  value: unknown
  expiresAt: string | null
  metadata: Record<string, unknown>
  resourceVersion: number
  createdAt: string
  updatedAt: string
}

export interface SecretBinding {
  namespace: string
  key: string
  provider: 'env'
  providerReference: string
  metadata: Record<string, unknown>
  resourceVersion: number
  inherited: boolean
  originNamespace: string
  createdAt: string
  updatedAt: string
}

export type PluginRegistryAttachmentKind = 'sbom' | 'vulnerability-report' | 'provenance'

export interface PluginRegistryPackage {
  name: string | null
  version: string | null
  bundle: string
  contentDigest: string
  manifest: {
    vendor: string
    license: string
    description: string | null
  } | null
  metadata: {
    license: string
    sourceUrl: string
    documentationUrl: string
    supportedPlatformRange: string
    sdkRange: string
    changelogUrl: string
  } | null
  attachments: Array<{
    kind: PluginRegistryAttachmentKind
    mediaType: string
    contentDigest: string
    signature: { keyId: string; algorithm: string; value: string }
  }>
  signals: {
    downloads: number
    lastMaintainedAt: string | null
    certification: 'unverified' | 'community' | 'verified' | 'certified'
    security: 'unknown' | 'current' | 'advisory' | 'critical'
    trustDisclaimer: string
  }
  artifactSignature: { keyId: string; algorithm: string; value: string } | null
  metadataSignature: { keyId: string; algorithm: string; value: string } | null
  publishedAt: string | null
  yanked: boolean
  yankedAt: string | null
  yankReason: string | null
}

export interface PluginRegistryIndex {
  schemaVersion: 'amesh.plugin-registry/v1'
  generatedAt: string
  packages: PluginRegistryPackage[]
  signature: { keyId: string; algorithm: string; value: string } | null
}
