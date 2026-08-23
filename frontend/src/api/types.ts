export type Capability =
  | 'assets.view'
  | 'assets.manage'
  | 'flows.view'
  | 'flows.create'
  | 'flows.update'
  | 'flowTests.view'
  | 'flowTests.manage'
  | 'flowTests.execute'
  | 'executions.view'
  | 'executions.execute'
  | 'executions.manage'
  | 'apps.view'
  | 'apps.manage'
  | 'apps.execute'
  | 'humanTasks.view'
  | 'humanTasks.update'
  | 'announcements.view'
  | 'operationalControls.manage'
  | 'dashboards.view'
  | 'dashboards.manage'
  | 'search.view'
  | 'search.manage'
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

export interface AppFormField {
  id: string
  type: string
  label: string
  helpText: string
  required: boolean
  sensitive: boolean
  placeholder: string | null
  default: unknown
  options: unknown[]
  validation: Record<string, unknown>
  schema: Record<string, unknown>
}

export interface AppFormSection {
  title: string
  helpText: string
  columns: number
  fields: string[]
}

export interface AppForm {
  fields: AppFormField[]
  layout: AppFormSection[]
}

export interface WorkflowApp {
  namespace: string
  appId: string
  title: string
  description: string
  flowId: string
  flowRevision: number
  form: AppForm
  embedEnabled: boolean
  launchLabel: string
  revision: number
  resourceVersion: number
  createdBy: string
  createdAt: string
}

export type HumanTaskState = 'OPEN' | 'ESCALATED' | 'APPROVED' | 'REJECTED' | 'CHANGES_REQUESTED'
export type HumanTaskActionKind = 'APPROVE' | 'REJECT' | 'REQUEST_CHANGES' | 'COMMENT' | 'ATTACH' | 'DELEGATE' | 'ESCALATE'

export interface HumanTaskAction {
  actionId: string
  action: HumanTaskActionKind
  actorId: string | null
  reason: string
  formValues: Record<string, unknown>
  comment: string
  artifactUri: string | null
  occurredAt: string
}

export interface HumanTask {
  humanTaskId: string
  namespace: string
  executionId: string
  taskRunId: string
  attempt: number
  title: string
  description: string
  form: AppForm
  assigneeIds: string[]
  groupIds: string[]
  deadlineAt: string | null
  state: HumanTaskState
  version: number
  createdAt: string
  decidedBy: string | null
  decidedAt: string | null
  reason: string
  formValues: Record<string, unknown>
  actions: HumanTaskAction[]
}

export interface HumanTaskNotification {
  notificationId: string
  humanTaskId: string
  kind: string
  title: string
  message: string
  deadlineAt: string | null
  createdAt: string
  readAt: string | null
}

export type AssetAccessMode = 'READ' | 'WRITE'
export type AssetHealth = 'UNKNOWN' | 'HEALTHY' | 'DEGRADED' | 'FAILED'
export type AssetRegistrationSource = 'DECLARED' | 'PLUGIN_EVENT'
export type LineageEvidenceKind = 'DECLARED' | 'OBSERVED' | 'INFERRED'

export interface AssetRecord {
  assetId: string
  tenantId: string
  namespace: string
  provider: string
  account: string
  location: string
  externalKey: string
  assetType: string
  displayName: string
  description: string
  owner: string | null
  contacts: string[]
  domainGroup: string | null
  tags: string[]
  customMetadata: Record<string, unknown>
  labels: Record<string, string>
  health: AssetHealth
  lastMaterializationAt: string | null
  source: AssetRegistrationSource
  resourceVersion: number
  createdBy: string
  updatedBy: string
  createdAt: string
  updatedAt: string
}

export type AssetDraft = Omit<AssetRecord, 'tenantId' | 'resourceVersion' | 'createdBy' | 'updatedBy' | 'createdAt' | 'updatedAt'>

export interface AssetObservation {
  observationId: string
  assetId: string
  tenantId: string
  namespace: string
  accessMode: AssetAccessMode
  evidenceKind: LineageEvidenceKind
  confidence: number
  flowId: string | null
  executionId: string | null
  taskRunId: string | null
  artifactId: string | null
  metadata: Record<string, unknown>
  observedAt: string
  createdBy: string
}

export interface AssetLineageEdge {
  edgeId: string
  tenantId: string
  namespace: string
  upstreamAssetId: string
  downstreamAssetId: string
  evidenceKind: LineageEvidenceKind
  confidence: number
  flowId: string | null
  executionId: string | null
  taskRunId: string | null
  artifactId: string | null
  metadata: Record<string, unknown>
  observedAt: string
  createdBy: string
}

export interface AssetCatalogEntry {
  asset: AssetRecord
  upstream: AssetRecord[]
  downstream: AssetRecord[]
  observations: AssetObservation[]
  edges: AssetLineageEdge[]
}

export type DashboardDataSource = 'EXECUTIONS' | 'LOGS' | 'METRICS' | 'SLA' | 'WORKERS' | 'ASSETS'
export type DashboardVisualization = 'TIME_SERIES' | 'TABLE' | 'COUNTER' | 'DISTRIBUTION' | 'STATUS_BREAKDOWN' | 'RANKED_LIST'
export type DashboardAggregation = 'COUNT' | 'SUM' | 'AVG' | 'MIN' | 'MAX' | 'P50' | 'P95'
export type DashboardMeasure = 'COUNT' | 'DURATION_MS' | 'VALUE'

export interface DashboardFilters {
  from?: string | null
  to?: string | null
  labels?: Record<string, string>
  namespace?: string | null
  flowId?: string | null
  states?: string[]
  workerGroups?: string[]
  dimensions?: Record<string, string>
}

export interface DashboardQuery {
  source: DashboardDataSource
  visualization: DashboardVisualization
  measure: DashboardMeasure
  aggregation: DashboardAggregation
  groupBy: string[]
  filters: DashboardFilters
  limit: number
  timeoutMs: number
  sampleRate: number
}

export interface DashboardWidget {
  widgetId: string
  title: string
  description: string
  query: DashboardQuery
}

export interface DashboardDefinition {
  dashboardId: string
  tenantId: string
  title: string
  description: string
  visibility: 'PRIVATE' | 'TENANT'
  viewerIds: string[]
  editorIds: string[]
  widgets: DashboardWidget[]
  source: 'BUILTIN' | 'API' | 'GITOPS'
  version: number
  ownerId: string
  builtin: boolean
  createdAt: string
  updatedAt: string
}

export interface DashboardSpec {
  title: string
  description: string
  visibility: 'PRIVATE' | 'TENANT'
  viewerIds: string[]
  editorIds: string[]
  widgets: DashboardWidget[]
  source: 'API' | 'GITOPS'
}

export interface DashboardQueryResult {
  columns: string[]
  rows: Array<Record<string, unknown>>
  freshAt: string
  partial: boolean
  sampled: boolean
  redacted: boolean
  scannedRows: number
  limit: number
}

export interface DashboardRender {
  dashboard: DashboardDefinition
  widgets: Array<{ widgetId: string; result: DashboardQueryResult }>
  renderedAt: string
}

export type SearchDocumentType = 'FLOW' | 'EXECUTION' | 'TASK_RUN' | 'LOG' | 'METRIC' | 'ASSET' | 'AUDIT'
export type SearchSortField = 'RELEVANCE' | 'TITLE' | 'OCCURRED_AT' | 'UPDATED_AT' | 'TYPE' | 'STATE'
export type SearchSortDirection = 'ASC' | 'DESC'
export type SearchRangeField = 'OCCURRED_AT' | 'UPDATED_AT' | 'SOURCE_VERSION'
export type SearchProjectionCondition = 'READY' | 'REBUILDING' | 'DEGRADED' | 'DISABLED'

export interface SearchRange {
  field: SearchRangeField
  gte?: string | number | null
  lte?: string | number | null
}

export interface SearchRequest {
  query?: string
  types?: SearchDocumentType[]
  namespace?: string | null
  states?: string[]
  labels?: Record<string, string>
  fields?: Record<string, string>
  from?: string | null
  to?: string | null
  ranges?: SearchRange[]
  sort?: SearchSortField
  direction?: SearchSortDirection
  limit?: number
  cursor?: string | null
}

export interface SearchDocument {
  documentType: SearchDocumentType
  documentId: string
  namespace: string | null
  title: string
  summary: string
  state: string | null
  labels: Record<string, string>
  fields: Record<string, unknown>
  occurredAt: string
  updatedAt: string
  sourceVersion: number
  relevance: number
}

export interface SearchResponse {
  items: SearchDocument[]
  nextCursor: string | null
  deniedTypes: SearchDocumentType[]
  projectionVersion: number
  projectionCondition: SearchProjectionCondition
  authoritativeFallback: boolean
}

export interface SearchProjectionStatus {
  projectionVersion: number
  schemaVersion: number
  buildingVersion: number | null
  condition: SearchProjectionCondition
  enabled: boolean
  documentsIndexed: number
  sourceDocuments: number
  progress: number
  lastProjectedAt: string | null
  latestSourceAt: string | null
  lagSeconds: number | null
  rebuildStartedAt: string | null
  rebuildCompletedAt: string | null
  failures: number
  lastError: string | null
  checkpointsVerified: boolean
  activeChecksum: string | null
}

export interface SearchProjectionVerificationItem {
  documentType: SearchDocumentType
  sourceCount: number
  projectedCount: number
  sourceChecksum: string
  projectedChecksum: string
  lastPosition: Record<string, unknown>
  verified: boolean
}

export interface SearchProjectionVerification {
  projectionVersion: number
  schemaVersion: number
  verified: boolean
  checksum: string
  items: SearchProjectionVerificationItem[]
  verifiedAt: string
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

export type FlowTestOutcome = 'PASSED' | 'FAILED' | 'ERROR'

export interface FlowTestDefinitionDraft {
  testId: string
  name: string
  revision: number
  inputs: Record<string, unknown>
  variables: Record<string, unknown>
  fixtures: Record<string, unknown>
  expected: Record<string, unknown>
  tags: string[]
  expectedVersion?: number
}

export interface FlowTestDefinition extends Omit<FlowTestDefinitionDraft, 'expectedVersion'> {
  id: string
  tenantId: string
  namespace: string
  flowId: string
  flowSemanticHash: string
  pluginSetHash: string
  version: number
  createdBy: string
  updatedBy: string
  createdAt: string
  updatedAt: string
}

export interface FlowTestCoverage {
  tasksTotal: number
  tasksCovered: number
  branchesTotal: number
  branchesCovered: number
  handlersTotal: number
  handlersCovered: number
  conditionsTotal: number
  conditionsCovered: number
  percentage: number
  disclaimer: string
}

export interface FlowTestAssertion {
  path: string
  passed: boolean
  expected: unknown
  actual: unknown
}

export interface FlowTestCaseResult {
  testId: string
  outcome: FlowTestOutcome
  state: string
  assertions: FlowTestAssertion[]
  error: string | null
}

export interface FlowTestRunResult {
  schemaVersion: string
  runId: string
  tenantId: string
  namespace: string
  flowId: string
  revision: number
  flowSemanticHash: string
  pluginSetHash: string
  simulatorVersion: string
  outcome: FlowTestOutcome
  cases: FlowTestCaseResult[]
  coverage: FlowTestCoverage
  isolated: boolean
  productionExecutionsCreated: number
  artifactsCreated: number
  secretLookups: number
  requestedBy: string
  createdAt: string
}

export interface FlowTestQualityGate {
  tenantId: string
  namespace: string
  enabled: boolean
  minimumCoverage: number
  requiredTestIds: string[]
  version: number
  updatedBy: string
  updatedAt: string
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

export type BlueprintCatalogSource = 'BUILTIN' | 'ORGANIZATION' | 'COMMUNITY'

export interface BlueprintParameter {
  name: string
  title: string
  description: string
  kind: 'STRING' | 'NAMESPACE' | 'FLOW_ID'
  required: boolean
  default: string | null
}

export interface BlueprintProvenance {
  publisher: string
  location: string
  revision: string
  digest: string
}

export interface BlueprintSummary {
  blueprintId: string
  version: string
  source: BlueprintCatalogSource
  title: string
  summary: string
  tags: string[]
  parameters: BlueprintParameter[]
  documentation: string
  license: string
  provenance: BlueprintProvenance
  localOnly: boolean
}

export interface BlueprintDefinition extends BlueprintSummary {
  template: string
}

export interface BlueprintDraftResponse {
  blueprint: BlueprintDefinition
  document: string
  validation: FlowValidationResult
}

export interface PlaygroundSimulationResponse {
  expressionResult: unknown
  redactedContext: Record<string, unknown>
  validation: FlowValidationResult | null
  steps: Array<{
    taskId: string
    taskType: string
    dependencies: string[]
    simulated: boolean
    reason: string
  }>
  safety: {
    persisted: false
    executed: false
    credentialAccess: false
    infrastructureAccess: false
  }
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

export interface ReadinessResponse extends HealthResponse {
  database: string
  migrations_applied: number
  migrations_expected: number
  latest_migration: string | null
  dependencies?: Record<string, string>
  degraded_dependencies?: string[]
  error: string | null
}

export interface PrincipalDefinition {
  id: string
  principal_type: 'USER' | 'GROUP' | 'SERVICE_ACCOUNT' | 'WORKER' | 'PLUGIN'
  handle: string
  display_name: string
  enabled: boolean
  metadata: { resource_version: number; lifecycle: string; created_at: string; updated_at: string }
}

export interface PermissionDefinition {
  resource_type: string
  action: string
  effect: 'ALLOW' | 'DENY'
}

export interface RoleDefinition {
  name: string
  display_name: string
  description: string
  built_in: boolean
  permissions: PermissionDefinition[]
}

export interface RoleBinding {
  id: string
  principal_id: string
  principal_type: PrincipalDefinition['principal_type']
  role_name: string
  scope_type: 'INSTANCE' | 'TENANT' | 'NAMESPACE'
  tenant_id: string | null
  namespace: string | null
}

export interface CredentialMetadata {
  id: string
  principal_id: string
  principal_type: PrincipalDefinition['principal_type']
  name: string
  kind: string
  scopes: string[]
  audience: string
  status: string
  expires_at: string
  rate_limit_per_minute: number
  last_used_at: string | null
  created_at: string
}

export interface IssuedCredential {
  metadata: CredentialMetadata
  token: string
}

export interface NamespaceWorkflowMetadataView {
  namespace: string
  lineage: Array<{
    tenantId: string
    namespace: string
    pluginDefaults: Array<{ type: string; values: Record<string, unknown>; forced?: boolean }>
    policy: Record<string, unknown>
    resourceVersion: number
    updatedBy: string
    updatedAt: string
  }>
}

export interface ServiceTopology {
  observedAt: string
  currentVersion: string
  versionSkew: boolean
  coordination: string
  quorumDependencies: Record<string, string>
  roles: Array<{
    role: string
    totalInstances: number
    liveInstances: number
    readyInstances: number
    drainingInstances: number
    staleInstances: number
    versions: string[]
    failoverStatus: string
  }>
  instances: Array<{
    id: string
    role: string
    instanceName: string
    version: string
    state: string
    liveness: string
    compatibility: string
    resourceVersion: number
    dependencies: Record<string, string>
    lastHeartbeatAt: string
  }>
}

export interface WorkerInventory {
  worker_id: string
  worker_group: string
  instance_name: string
  version: string
  status: string
  liveness: string
  compatibility: string
  capacity: number
  claimed_work: number
  utilization: number
  last_heartbeat_at: string
}

export interface AdmissionDiagnostics {
  active_reservations: number
  queued_requests: number
  oldest_queue_age_seconds: number
  pressure_by_policy: Record<string, number>
}

export interface NetworkDiagnosticBundle {
  schemaVersion: number
  generatedAt: string
  inboundTlsMode: 'disabled' | 'direct' | 'trusted-proxy'
  minimumTlsVersion: 'TLSv1.2' | 'TLSv1.3'
  clientAuthentication: 'none' | 'optional' | 'required'
  topology: 'compact' | 'split'
  privateEndpoint: boolean
  externalBaseUrl: string | null
  trustedProxyRanges: string[]
  httpProxyConfigured: boolean
  httpsProxyConfigured: boolean
  noProxy: string[]
  egressAllowedHosts: string[]
  allowedPrivateHosts: string[]
  connections: Array<{
    name: string
    scheme: string
    host: string
    port: number | null
    proxy: 'HTTP' | 'HTTPS' | 'BYPASSED' | 'DIRECT'
  }>
  certificates: Array<{
    purpose: string
    configured: boolean
    status: 'NOT_CONFIGURED' | 'READY' | 'MISSING' | 'INVALID'
    fingerprint: string | null
    modifiedAt: string | null
    detail: string
  }>
  dns: Array<{
    host: string
    status: 'RESOLVED' | 'FAILED'
    addresses: string[]
    detail: string
  }>
}

export interface ConfigurationSnapshot {
  schema_version: number
  version: number
  fingerprint: string
  loaded_at: string
  precedence: string[]
  entries: Array<{ name: string; value: unknown; source: string; reloadable: boolean; secret: boolean }>
  warnings: string[]
}

export interface FeatureFlag {
  id: string
  key: string
  scope: 'INSTANCE' | 'TENANT' | 'NAMESPACE'
  enabled: boolean
  tenant_id: string | null
  namespace: string | null
  description: string
  version: number
  updated_by: string
  updated_at: string
}

export type AdministrationControlKey = 'RETENTION' | 'ANNOUNCEMENT' | 'MAINTENANCE' | 'KILL_SWITCH'

export interface AdministrationControlDraft {
  key: AdministrationControlKey
  enabled: boolean
  value: string | number | null
  reason: string
  expectedVersion?: number | null
}

export interface AdministrationControl {
  key: AdministrationControlKey
  flagKey: string
  enabled: boolean
  value: string | number | null
  version: number | null
  updatedBy: string | null
  updatedAt: string | null
}

export interface AdministrationImpactPreview {
  draft: AdministrationControlDraft
  impacts: string[]
  recovery: string
  confirmation: string
  approval: string
  expiresAt: string
}

export interface AdministrationAuditEntry {
  eventId: string
  actorId: string
  action: string
  resourceId: string
  outcome: 'SUCCESS' | 'REJECTED'
  reason: string
  evidence: Record<string, unknown>
  occurredAt: string
}

export type AnnouncementSeverity = 'INFO' | 'WARNING' | 'CRITICAL'
export type AnnouncementAudience = 'INSTANCE' | 'TENANT' | 'NAMESPACE'

export interface Announcement {
  id: string
  tenantId: string | null
  title: string
  message: string
  severity: AnnouncementSeverity
  audience: AnnouncementAudience
  namespace: string | null
  startsAt: string
  expiresAt: string
  active: boolean
  version: number
  createdBy: string
  createdAt: string
  updatedAt: string
}

export interface AnnouncementDraft {
  title: string
  message: string
  severity: AnnouncementSeverity
  audience: AnnouncementAudience
  namespace?: string | null
  startsAt: string
  expiresAt: string
}

export type OperationalBoundary = 'AUTHORING' | 'NEW_EXECUTIONS' | 'TRIGGERS' | 'API_WRITES' | 'WORKER_DISPATCH'
export type OperationalControlScope = 'INSTANCE' | 'TENANT' | 'NAMESPACE' | 'FLOW' | 'PLUGIN' | 'RUNNER'
export type RunningWorkPolicy = 'CONTINUE' | 'DRAIN' | 'CANCEL'

export interface OperationalControlAcknowledgement {
  componentId: string
  componentRole: string
  controlVersion: number
  acknowledgedAt: string
}

export interface OperationalControl {
  id: string
  tenantId: string | null
  kind: 'MAINTENANCE' | 'KILL_SWITCH'
  name: string
  scope: OperationalControlScope
  namespace: string | null
  flowId: string | null
  pluginId: string | null
  runnerId: string | null
  boundaries: OperationalBoundary[]
  runningWorkPolicy: RunningWorkPolicy
  reason: string
  state: 'ACTIVE' | 'BYPASSED' | 'DEACTIVATED' | 'EXPIRED'
  version: number
  expiresAt: string | null
  reviewAt: string | null
  bypassUntil: string | null
  bypassReason: string | null
  createdBy: string
  updatedBy: string
  createdAt: string
  updatedAt: string
  acknowledgements: OperationalControlAcknowledgement[]
}

export interface OperationalControlDraft {
  kind: OperationalControl['kind']
  name: string
  scope: OperationalControlScope
  namespace?: string | null
  flowId?: string | null
  pluginId?: string | null
  runnerId?: string | null
  boundaries: OperationalBoundary[]
  runningWorkPolicy: RunningWorkPolicy
  reason: string
  expiresAt?: string | null
  reviewAt?: string | null
}

export interface OperationalControlAction {
  action: 'EXTEND' | 'BYPASS' | 'DEACTIVATE'
  reason: string
  expectedVersion: number
  expiresAt?: string | null
  reviewAt?: string | null
  bypassUntil?: string | null
}

export interface OperationalControlEvent {
  eventId: string
  controlId: string
  action: string
  actorId: string
  reason: string
  evidence: Record<string, unknown>
  occurredAt: string
}

export interface AuthenticationProvider {
  id: string
  kind: string
  display_name: string
  interactive: boolean
  login_mode?: 'password' | 'redirect'
  domains?: string[]
  tenants?: string[]
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

export type PluginPolicyScope = 'INSTANCE' | 'TENANT' | 'NAMESPACE'
export type PluginPolicyStage = 'AUTHORING' | 'VALIDATION' | 'EXECUTION' | 'ADMINISTRATION'

export interface PluginPolicyRuleDraft {
  scope: PluginPolicyScope
  namespace?: string | null
  effect: 'ALLOW' | 'DENY'
  stages: PluginPolicyStage[]
  selector: {
    package: string
    versionRange: string
    vendor: string
    pluginTypes: string[]
    capabilities: string[]
  }
  priority: number
  reason: string
  enabled: boolean
}

export interface PluginPolicyRule extends PluginPolicyRuleDraft {
  id: string
  tenantId: string | null
  createdBy: string
  createdAt: string
  updatedBy: string
  updatedAt: string
}

export interface PluginQuarantineDraft {
  scope: PluginPolicyScope
  namespace?: string | null
  package: string
  version: string
  reason: string
}

export interface PluginQuarantine extends PluginQuarantineDraft {
  id: string
  tenantId: string | null
  state: 'ACTIVE' | 'RELEASED'
  createdBy: string
  createdAt: string
  releasedBy: string | null
  releasedAt: string | null
}

export interface EffectivePluginPolicy {
  tenantId: string
  namespace: string | null
  defaultEffect: 'ALLOW' | 'DENY'
  rules: PluginPolicyRule[]
  quarantines: PluginQuarantine[]
}

export interface PluginPolicyImpactPreview {
  package: string
  version: string
  affectedFlows: Array<Record<string, unknown>>
  runningExecutions: Array<Record<string, unknown>>
}

export type LifecycleResourceType = 'EXECUTION' | 'LOG' | 'METRIC' | 'ARTIFACT' | 'CACHE'
export type LifecycleScope = 'INSTANCE' | 'TENANT' | 'NAMESPACE' | 'LABEL'

export interface LifecyclePolicyDraft {
  resourceType: LifecycleResourceType
  scope: LifecycleScope
  namespace?: string | null
  labelSelector: Record<string, string>
  retentionDays: number
  batchSize: number
  scheduleIntervalMinutes?: number | null
  enabled: boolean
  reason: string
}

export interface LifecyclePolicy extends LifecyclePolicyDraft {
  id: string
  tenantId: string | null
  nextRunAt: string | null
  createdBy: string
  createdAt: string
  updatedBy: string
  updatedAt: string
  version: number
}

export interface LifecycleLegalHoldDraft {
  name: string
  reason: string
  resourceType?: LifecycleResourceType | null
  resourceId?: string | null
  namespace?: string | null
  labelSelector: Record<string, string>
  dataFrom?: string | null
  dataTo?: string | null
}

export interface LifecycleLegalHold extends LifecycleLegalHoldDraft {
  id: string
  tenantId: string
  active: boolean
  createdBy: string
  createdAt: string
  releasedBy: string | null
  releasedAt: string | null
}

export interface LifecycleJob {
  id: string
  tenantId: string
  policyId: string
  trigger: 'MANUAL' | 'SCHEDULED'
  state: 'PREVIEWED' | 'READY' | 'RUNNING' | 'WAITING_EXTERNAL' | 'SUCCEEDED' | 'FAILED'
  cutoff: string
  policySnapshot: LifecyclePolicyDraft & { id: string; version: number }
  estimatedRecords: number
  estimatedBytes: number
  protectedRecords: number
  activeRecords: number
  processedRecords: number
  processedBytes: number
  batchSize: number
  cursor: string | null
  retryCount: number
  lastError: string | null
  evidence: Record<string, unknown>
  reason: string
  actorId: string
  previewExpiresAt: string
  startedAt: string | null
  completedAt: string | null
  createdAt: string
  updatedAt: string
  confirmationPhrase: string
}

export interface UpgradeRelease {
  version: string
  lts: boolean
  supportStartsOn: string
  supportEndsOn: string
  schemaMigration: string
  minimumComponents: Record<string, string>
}

export interface UpgradePath {
  fromVersion: string
  toVersion: string
  rollingCompatible: boolean
  messageSchemaVersions: number[]
  rollbackWindowHours: number
  restorationGuidance: string
}

export interface UpgradePolicy {
  schemaVersion: 'amesh.upgrade-policy/v1'
  currentVersion: string
  capacityThresholds: {
    maximumDatabaseBytes: number
    maximumQueuedWork: number
    maximumActiveExecutions: number
  }
  releases: UpgradeRelease[]
  paths: UpgradePath[]
}

export interface UpgradeCheck {
  name: string
  category: string
  status: 'PASS' | 'WARNING' | 'BLOCKED'
  detail: string
  remediation: string | null
  evidence: Record<string, unknown>
}

export interface UpgradeReport {
  id: string
  phase: 'PRE_UPGRADE' | 'POST_UPGRADE'
  fromVersion: string
  toVersion: string
  observedAt: string
  safeToProceed: boolean
  rollingCompatible: boolean
  checks: UpgradeCheck[]
  warnings: string[]
  rollingPlan: Array<{ order: number; role: string; action: string; verification: string }>
  restorationGuidance: string
  reportFingerprint: string
}

export interface PersistedEventMigration {
  eligibleEvents: number
  migratedEvents: number
  remainingEvents: number
  confirmationPhrase: string
  applied: boolean
  evidenceEventId: string | null
}
