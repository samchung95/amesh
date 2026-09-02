import type { components } from './generated/openapi'

export type Capability =
  | 'assets.view'
  | 'assets.manage'
  | 'agents.view'
  | 'agents.manage'
  | 'agents.execute'
  | 'flows.view'
  | 'flows.create'
  | 'flows.update'
  | 'flowTests.view'
  | 'flowTests.manage'
  | 'flowTests.execute'
  | 'executions.view'
  | 'executions.execute'
  | 'executions.manage'
  | 'agentSessions.view'
  | 'agentSessions.create'
  | 'agentSessions.list'
  | 'agentSessionPolicies.view'
  | 'agentSessionPolicies.manage'
  | 'agentSessionMigration.view'
  | 'agentSessionMigration.manage'
  | 'agentSessionAdministration.view'
  | 'agentSessionAdministration.instanceView'
  | 'agentSessions.manage'
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
  | 'releases.view'
  | 'releases.manage'
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

export type PromotionTargetKind = components["schemas"]["PromotionTargetKind"];

export interface PromotionGate {
  gateId: string
  tenantId: string
  policyId: string
  policyDigest: string
  targetKind: PromotionTargetKind
  targetKey: string
  targetRevision: number
  configurationDigest: string
  evidenceDigests: string[]
  passed: boolean
  failures: string[]
  evaluatedAt: string
}

export interface ReleaseTarget {
  tenantId: string
  targetKind: PromotionTargetKind
  targetKey: string
  activeRevision: number | null
  activeConfigurationDigest: string | null
  state: 'ACTIVE' | 'KILLED'
  version: number
  updatedAt: string
}

export interface ReleaseHistoryEntry {
  eventId: string
  tenantId: string
  targetKind: PromotionTargetKind
  targetKey: string
  action: 'PROMOTE' | 'ROLLBACK' | 'KILL_SWITCH'
  fromRevision: number | null
  toRevision: number | null
  toConfigurationDigest: string | null
  gateDigest: string | null
  actorId: string
  reason: string
  version: number
  occurredAt: string
}

export interface ReleaseActionResult {
  target: ReleaseTarget
  event: ReleaseHistoryEntry
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

export type AppForm = Omit<components["schemas"]["AppForm"], 'fields' | 'layout'> & {
  fields: AppFormField[]
  layout: AppFormSection[]
}

export type WorkflowApp = Omit<components["schemas"]["WorkflowApp"], 'form'> & {
  form: AppForm
}
export type HumanTaskState = components["schemas"]["HumanTaskState"];
export type HumanTaskActionKind = components["schemas"]["HumanTaskActionKind"];
export type HumanTaskAction = components["schemas"]["HumanTaskAction"];
export type HumanTask = Omit<components["schemas"]["HumanTask"], 'form'> & {
  form: AppForm
}
export type HumanTaskNotification = components["schemas"]["HumanTaskNotification"];
export type AssetAccessMode = components["schemas"]["AssetAccessMode"];
export type AssetHealth = components["schemas"]["AssetHealth"];
export type AssetRegistrationSource = components["schemas"]["AssetRegistrationSource"];
export type LineageEvidenceKind = components["schemas"]["LineageEvidenceKind"];
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

export type AssetObservation = components["schemas"]["AssetObservation"];
export type AssetLineageEdge = components["schemas"]["AssetLineageEdge"];
export type AssetCatalogEntry = components["schemas"]["AssetCatalogEntry"];
export type DashboardDataSource = components["schemas"]["DashboardDataSource"];
export type DashboardVisualization = components["schemas"]["DashboardVisualization"];
export type DashboardAggregation = components["schemas"]["DashboardAggregation"];
export type DashboardMeasure = components["schemas"]["DashboardMeasure"];
export type DashboardFilters = Omit<components["schemas"]["DashboardFilters"], 'states' | 'workerGroups'> & {
  states?: string[]
  workerGroups?: string[]
};
export type DashboardQuery = Omit<components["schemas"]["DashboardQuery"], 'filters'> & {
  filters: DashboardFilters
}
export type DashboardWidget = Omit<components["schemas"]["DashboardWidget"], 'query'> & {
  query: DashboardQuery
}
export type DashboardDefinition = Omit<components["schemas"]["DashboardDefinition"], 'widgets'> & {
  widgets: DashboardWidget[]
}
export type DashboardSpec = Omit<components["schemas"]["DashboardSpec"], 'widgets' | 'source'> & {
  widgets: DashboardWidget[]
  source: 'API' | 'GITOPS'
}
export type DashboardQueryResult = components["schemas"]["DashboardQueryResult"];
export type DashboardRender = Omit<components["schemas"]["DashboardRender"], 'dashboard'> & {
  dashboard: DashboardDefinition
}
export type SearchDocumentType = components["schemas"]["SearchDocumentType"];
export type SearchSortField = components["schemas"]["SearchSortField"];
export type SearchSortDirection = components["schemas"]["SearchSortDirection"];
export type SearchRangeField = components["schemas"]["SearchRangeField"];
export type SearchProjectionCondition = components["schemas"]["SearchProjectionCondition"];

export type SearchRange = components["schemas"]["SearchRange"];

export type SearchRequest = Partial<components["schemas"]["SearchRequest"]>;

export type SearchDocument = Omit<components["schemas"]["SearchDocument"], 'fields' | 'labels'> & {
  fields: Record<string, unknown>
  labels: Record<string, string>
}

export type SearchResponse = Omit<components["schemas"]["SearchResponse"], 'items'> & {
  items: SearchDocument[]
}

export type SearchProjectionStatus = components["schemas"]["SearchProjectionStatus"];

export type SearchProjectionVerificationItem = components["schemas"]["SearchProjectionVerificationItem"];

export type SearchProjectionVerification = components["schemas"]["SearchProjectionVerification"];

export type PersistedFlow = components["schemas"]["PersistedFlow"];
export type SourcePosition = components["schemas"]["SourcePosition"];

export interface FlowValidationIssue {
  code: string
  message: string
  path: string
  hint: string
  sourceRange: { start: SourcePosition; end: SourcePosition } | null
  severity: string
}

export type FlowValidationResult = Omit<components["schemas"]["FlowValidationResult"], 'irVersion' | 'semantic_hash' | 'canonical' | 'issues'> & {
  irVersion: 'amesh.flow/v1' | null
  semantic_hash: string | null
  canonical: Record<string, unknown> | null
  issues: FlowValidationIssue[]
};
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

export type FlowDocumentExport = components["schemas"]["FlowDocumentExport"];
export type FlowRevisionRecord = components["schemas"]["FlowRevisionRecord"];
export type FlowRevisionDiff = components["schemas"]["FlowRevisionDiff"];
export type FlowTestOutcome = components["schemas"]["FlowTestOutcome"];
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

export type FlowTestDefinition = components["schemas"]["FlowTestDefinition"];
export type FlowTestCoverage = components["schemas"]["FlowTestCoverage"];
export type FlowTestAssertion = components["schemas"]["FlowTestAssertion"];
export type FlowTestCaseResult = components["schemas"]["FlowTestCaseResult"];
export type FlowTestRunResult = components["schemas"]["FlowTestRunResult"];
export type FlowTestQualityGate = components["schemas"]["FlowTestQualityGate"];
export type SimulationTaskPlan = components["schemas"]["SimulationTaskPlan"];

export type DeterminismPolicyPin = Omit<components["schemas"]["DeterminismPolicyPin"], 'revision'> & {
  revision: number | null
}
export type DeterminismNode = components["schemas"]["DeterminismNode"];
export type DynamicExecutionBound = components["schemas"]["DynamicExecutionBound"];
export type DeterminismEnvelope = Omit<components["schemas"]["DeterminismEnvelope"], 'policyPins'> & {
  policyPins: DeterminismPolicyPin[]
}
export type SimulationPlan = Omit<components["schemas"]["SimulationPlan"], 'estimates' | 'deterministicEnvelope'> & {
  deterministicEnvelope: DeterminismEnvelope
  estimates: Omit<components["schemas"]["SimulationPlan"]['estimates'], 'runnerDemand'> & {
    runnerDemand: Record<string, number>
  }
}

export type FlowFormatResponse = Omit<components["schemas"]["FlowFormatResponse"], 'validation'> & {
  validation: FlowValidationResult
}
export type ExpressionPreviewResponse = components["schemas"]["ExpressionPreviewResponse"];
export type BlueprintCatalogSource = components["schemas"]["BlueprintCatalogSource"];
export type BlueprintParameter = components["schemas"]["BlueprintParameter"];
export type BlueprintProvenance = components["schemas"]["BlueprintProvenance"];
export type BlueprintSummary = components["schemas"]["BlueprintSummary"];
export type BlueprintDefinition = components["schemas"]["BlueprintDefinition"];
export type BlueprintDraftResponse = components["schemas"]["BlueprintDraftResponse"];
export type PlaygroundSimulationResponse = Omit<components["schemas"]["PlaygroundSimulationResponse"], 'expressionResult' | 'redactedContext' | 'validation' | 'safety'> & {
  expressionResult: unknown
  redactedContext: Record<string, unknown>
  validation: FlowValidationResult | null
  safety: {
    persisted: false
    executed: false
    credentialAccess: false
    infrastructureAccess: false
  }
};
export type ExecutionState = components["schemas"]["ExecutionState"];
export type ExecutionRunner = 'local' | 'docker' | 'kubernetes'

export type PersistedExecution = Omit<components["schemas"]["PersistedExecution"], 'inputs' | 'outputs' | 'labels' | 'trigger' | 'timeout_at' | 'cancel_deadline_at' | 'lifecycle_evidence'> & {
  inputs: Record<string, unknown>
  outputs: Record<string, unknown>
  labels: Record<string, string>
  trigger: Record<string, unknown>
  timeout_at: string | null
  cancel_deadline_at: string | null
  lifecycle_evidence: Record<string, unknown>
};
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

export type FlowDataContract = Omit<components["schemas"]["FlowDataContract"], 'inputSchema' | 'outputs' | 'variables'> & {
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
};
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

export type PersistedTaskRun = Omit<components["schemas"]["PersistedTaskRun"], 'retry_at' | 'result' | 'iteration_key' | 'labels' | 'failure_category' | 'evidence'> & {
  retry_at: string | null
  result: Record<string, unknown> | null
  iteration_key: string | null
  labels: Record<string, string>
  failure_category: string | null
  evidence: Record<string, unknown>
};
export type ExecutionDetail = Omit<components["schemas"]["ExecutionDetail"], 'execution' | 'taskRuns' | 'taskRunSummary'> & {
  execution: PersistedExecution
  taskRuns: PersistedTaskRun[]
  taskRunSummary: TaskRunSummary | null
};
export interface TaskRunSummary {
  total: number
  waiting: number
  running: number
  retry_delay: number
  succeeded: number
  failed: number
  cancelled: number
}

export type ExecutionEvidenceKind = components["schemas"]["ExecutionEvidenceKind"];
export type ExecutionEvidenceEvent = Omit<components["schemas"]["ExecutionEvidenceEvent"], 'task_run_id' | 'payload'> & {
  task_run_id: string | null
  payload: Record<string, unknown>
};
export type ExecutionEvidencePage = Omit<components["schemas"]["ExecutionEvidencePage"], 'nextCursor' | 'items'> & {
  items: ExecutionEvidenceEvent[]
  nextCursor: string | null
};
export interface ExecutionEvidenceStreamEvent extends ExecutionEvidenceEvent {
  nextCursor: string
}

export type ExecutionInterventionAction = components["schemas"]["ExecutionInterventionAction"];
export type ExecutionInterventionPreview = Omit<components["schemas"]["ExecutionInterventionPreview"], 'checkpoint_task_id' | 'force_available_at'> & {
  checkpoint_task_id: string | null
  force_available_at: string | null
};
export type ExecutionInterventionRecord = components["schemas"]["ExecutionInterventionRecord"];
export type PersistedSubflow = Omit<components["schemas"]["PersistedSubflow"], 'propagation'>;
export type ExecutionArtifact = components["schemas"]["ExecutionArtifact"];
export type BackfillSpec = Omit<components["schemas"]["BackfillSpec"], 'selection' | 'inputs' | 'replaySources' | 'labels'> & {
  namespace: string
  selection: {
    sourceExecutionIds?: string[]
    timeRange?: { start: string; end: string; intervalSeconds: number }
  }
  inputs: Record<string, unknown>
  replaySources?: Array<{
    sourceExecutionId: string
    frozenInputDigest: string
    resourcePins: Array<{ key: string; revision: number; digest: string }>
  }>
  labels: Record<string, string>
};
export type BackfillPreview = components["schemas"]["BackfillPreview"];
export type BackfillRecord = components["schemas"]["BackfillRecord"];
export type TriggerOccurrenceState = components["schemas"]["TriggerOccurrenceState"];

export type TriggerRuntimeState = components["schemas"]["TriggerRuntimeState"];

export type TriggerOccurrence = Omit<components["schemas"]["TriggerOccurrence"], 'payload' | 'metadata' | 'evidence' | 'execution_id' | 'replay_of' | 'completed_at'> & {
  payload: Record<string, unknown>
  metadata: Record<string, unknown>
  evidence: Record<string, unknown>
  execution_id: string | null
  replay_of: string | null
  completed_at: string | null
}

export type CheckOutcome = components["schemas"]["CheckOutcome"];
export type CheckEvaluation = components["schemas"]["CheckEvaluation"];
export type CheckComplianceSummary = components["schemas"]["CheckComplianceSummary"];
export type NamespaceCheckPolicy = components["schemas"]["NamespaceCheckPolicy"];
export type FlowGraphNode = components["schemas"]["FlowGraphNode"];
export type FlowGraphEdge = components["schemas"]["FlowGraphEdge"];
export type FlowGraph = components["schemas"]["FlowGraph"];
export type HealthResponse = components["schemas"]["HealthResponse"];
export type ReadinessResponse = Omit<components["schemas"]["ReadinessResponse"], 'degraded_dependencies'> & {
  degraded_dependencies?: string[]
}

export type PrincipalDefinition = Omit<components["schemas"]["PrincipalDefinition"], 'id' | 'principal_type' | 'handle' | 'display_name' | 'enabled' | 'metadata'> & {
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

export type RoleDefinition = components["schemas"]["RoleDefinition"];

export type RoleBinding = Omit<components["schemas"]["RoleBinding"], 'id' | 'principal_id' | 'principal_type' | 'role_name' | 'scope_type' | 'tenant_id' | 'namespace'> & {
  id: string
  principal_id: string
  principal_type: PrincipalDefinition['principal_type']
  role_name: string
  scope_type: 'INSTANCE' | 'TENANT' | 'NAMESPACE'
  tenant_id: string | null
  namespace: string | null
}

export type CredentialMetadata = components["schemas"]["CredentialMetadata"];
export interface IssuedCredential {
  metadata: CredentialMetadata
  token: string
}

export type NamespaceWorkflowMetadataView = Omit<components["schemas"]["NamespaceWorkflowMetadataView"], 'lineage'> & {
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
export type ServiceTopology = components["schemas"]["ServiceTopology"];

export type WorkerInventory = components["schemas"]["WorkerInventory"];
export type AdmissionDiagnostics = components["schemas"]["AdmissionDiagnostics"];
export type NetworkDiagnosticBundle = components["schemas"]["NetworkDiagnosticBundle"];
export type ConfigurationSnapshot = components["schemas"]["ConfigurationSnapshot"];
export type FeatureFlag = components["schemas"]["FeatureFlag"];
export type AdministrationControlKey = components["schemas"]["AdministrationControlKey"];
export type AdministrationControlDraft = components["schemas"]["AdministrationControlDraft"];
export type AdministrationControl = components["schemas"]["AdministrationControl"];
export type AdministrationImpactPreview = components["schemas"]["AdministrationImpactPreview"];
export type AdministrationAuditEntry = components["schemas"]["AdministrationAuditEntry"];
export type AnnouncementSeverity = components["schemas"]["AnnouncementSeverity"];
export type AnnouncementAudience = components["schemas"]["AnnouncementAudience"];
export type Announcement = components["schemas"]["Announcement"] & {
  id: string
  version: number
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

export type OperationalBoundary = components["schemas"]["OperationalBoundary"];
export type OperationalControlScope = components["schemas"]["OperationalControlScope"];
export type RunningWorkPolicy = components["schemas"]["RunningWorkPolicy"];

export type OperationalControlAcknowledgement = components["schemas"]["OperationalControlAcknowledgement"];
export type OperationalControl = components["schemas"]["OperationalControl"] & {
  id: string
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

export type OperationalControlEvent = components["schemas"]["OperationalControlEvent"];
export interface AuthenticationProvider {
  id: string
  kind: string
  display_name: string
  interactive: boolean
  login_mode?: 'password' | 'redirect'
  domains?: string[]
  tenants?: string[]
}

export type LoginResponse = components["schemas"]["LoginResponse"];
export type NamespaceFile = components["schemas"]["NamespaceFile"];
export type ImageArtifactRef = Omit<components["schemas"]["ImageArtifactRef"], 'artifact' | 'display'> & {
  artifact: {
    reference: string
    contentAddress: string
    tenantId: string
    namespace: string
    path: string
    version: number
    mediaType: string | null
    sizeBytes: number
    checksumSha256: string
    provenance: Record<string, unknown>
    retention: Record<string, unknown>
  }
  display: {
    filename: string | null
    altText: string | null
    widthPixels: number
    heightPixels: number
  }
}
export type NamespaceFileVersion = components["schemas"]["NamespaceFileVersion"];
export type ArtifactRef = components["schemas"]["ArtifactRef"];
export type KeyValueType = components["schemas"]["KeyValueType"];
export type KeyValueEntry = components["schemas"]["KeyValueEntry"];
export type SecretBinding = components["schemas"]["SecretBinding"];

export type PluginRegistryAttachmentKind = components["schemas"]["PluginRegistryAttachmentKind"];

export type PluginRegistryPackage = Omit<components["schemas"]["PluginRegistryPackage"], 'signals'> & {
  signals: {
    downloads: number
    lastMaintainedAt: string | null
    certification: 'unverified' | 'community' | 'verified' | 'certified'
    security: 'unknown' | 'current' | 'advisory' | 'critical'
    trustDisclaimer: string
  }
}

export type PluginRegistryIndex = Omit<components["schemas"]["PluginRegistryIndex"], 'packages'> & {
  packages: PluginRegistryPackage[]
}

export type PluginPolicyScope = components["schemas"]["PluginPolicyScope"];
export type PluginPolicyStage = components["schemas"]["PluginPolicyStage"];

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

export type PluginPolicyRule = Omit<components["schemas"]["PluginPolicyRule"], 'id' | 'selector'> & {
  id: string
  selector: PluginPolicyRuleDraft['selector']
}

export interface PluginQuarantineDraft {
  scope: PluginPolicyScope
  namespace?: string | null
  package: string
  version: string
  reason: string
}

export type PluginQuarantine = components["schemas"]["PluginQuarantine"];

export type EffectivePluginPolicy = Omit<components["schemas"]["EffectivePluginPolicy"], 'rules'> & {
  rules: PluginPolicyRule[]
}
export type PluginPolicyImpactPreview = components["schemas"]["PluginPolicyImpactPreview"];

export type AdmissionPolicyStage = 'VALIDATE' | 'SAVE' | 'PROMOTE' | 'LAUNCH' | 'DISPATCH'
export type AdmissionPolicyOutcome = 'ALLOW' | 'DENY' | 'WARN' | 'MUTATE_DEFAULT' | 'REQUIRE_APPROVAL'
export type AdmissionPolicyOperator = 'EQUALS' | 'NOT_EQUALS' | 'IN' | 'CONTAINS' | 'EXISTS' | 'MATCHES' | 'LESS_THAN' | 'LESS_THAN_OR_EQUAL' | 'GREATER_THAN' | 'GREATER_THAN_OR_EQUAL'

export interface AdmissionPolicyDocument {
  schemaVersion: 'amesh.policy/v1'
  policyKey: string
  name: string
  description: string
  scope: PluginPolicyScope
  namespace?: string | null
  criticality: 'ADVISORY' | 'ENFORCING'
  evaluationTimeoutMs: number
  enabled: boolean
  rules: Array<{
    id: string
    stages: AdmissionPolicyStage[]
    conditions: Array<{ path: string; operator: AdmissionPolicyOperator; value: unknown }>
    outcome: AdmissionPolicyOutcome
    reason: string
    mutations: Record<string, unknown>
  }>
}

export interface AdmissionPolicyRevision {
  policyId: string
  tenantId: string | null
  revision: number
  digest: string
  document: AdmissionPolicyDocument
  createdBy: string
  createdAt: string
}

export interface AdmissionPolicyDecision {
  id: string
  engineVersion: string
  stage: AdmissionPolicyStage
  outcome: AdmissionPolicyOutcome
  allowed: boolean
  tenantId: string
  namespace: string
  actorId: string
  flowId: string
  flowRevision: number
  pinnedPolicies: Array<{ policyId: string; policyKey: string; revision: number; digest: string }>
  matchedRules: Array<{
    policyId: string
    policyKey: string
    policyRevision: number
    ruleId: string
    outcome: AdmissionPolicyOutcome
    reason: string
    approvalKey: string | null
    conditions: Array<{ path: string; operator: AdmissionPolicyOperator; expected: unknown; actual: unknown; matched: boolean }>
  }>
  warnings: string[]
  mutations: Array<{ path: string; value: unknown; applied: boolean }>
  requiredApprovals: string[]
  inputHash: string
  evaluationDurationMs: number
  evaluationLimitMs: number
  decidedAt: string
}

export type LifecycleResourceType = components["schemas"]["LifecycleResourceType"];
export type LifecycleScope = components["schemas"]["LifecycleScope"];
export type LifecyclePolicyDraft = Omit<components["schemas"]["LifecyclePolicyDraft"], 'labelSelector'> & {
  labelSelector: Record<string, string>
}
export type LifecyclePolicy = Omit<components["schemas"]["LifecyclePolicy"], 'labelSelector'> & {
  labelSelector: Record<string, string>
}
export type LifecycleLegalHoldDraft = components["schemas"]["LifecycleLegalHoldDraft"];
export type LifecycleLegalHold = components["schemas"]["LifecycleLegalHold"];
export type LifecycleJob = Omit<components["schemas"]["LifecycleJob"], 'policySnapshot'> & {
  policySnapshot: LifecyclePolicyDraft & { id: string; version: number }
}
export type UpgradeRelease = components["schemas"]["UpgradeRelease"];
export type UpgradePath = components["schemas"]["UpgradePath"];
export type UpgradePolicy = components["schemas"]["UpgradePolicy"];
export type UpgradeCheck = components["schemas"]["UpgradeCheck"];
export type UpgradeReport = components["schemas"]["UpgradeReport"];
export type PersistedEventMigration = components["schemas"]["PersistedEventMigration"];
export type AgentResourceKind = components["schemas"]["AgentResourceKind"];
export type AgentCapabilityKind = 'prompt' | 'skill' | 'model-policy' | 'evaluation' | 'agent' | 'plugin' | 'mcp-connection' | 'mcp-tool'
export type AgentCapabilityStatus = 'available' | 'deprecated' | 'incompatible' | 'unavailable' | 'denied' | 'schema-drift' | 'yanked'

export interface AgentCapabilityPermissions {
  delegatedCapabilities: string[]
  toolAllowlist: string[]
  secretScopes: string[]
  networkHosts: string[]
  allowedEgress: string[]
  filesystemReadRoots: string[]
  filesystemWriteRoots: string[]
  allowHighImpact: boolean
}

export interface AgentCapabilityReference {
  kind: AgentCapabilityKind
  key: string
  revision: number | string
  digest: string
  providerKind?: string | null
  providerKey?: string | null
  providerRevision?: number | null
  providerDigest?: string | null
  connectionKey?: string | null
  connectionRevision?: number | null
  connectionDigest?: string | null
  toolName?: string | null
  schemaDigest?: string | null
}

export interface AgentCapabilityAttachment {
  target: 'agent-definition' | 'workflow' | 'none'
  reference: AgentCapabilityReference | null
  constraints: string[]
}

export interface AgentCapabilityCatalogItem {
  kind: AgentCapabilityKind
  catalogId: string
  key: string
  humanLabel: string
  revision: number | string
  digest: string
  status: AgentCapabilityStatus
  description: string
  schemas: Record<string, unknown>
  impact: 'NONE' | 'READ_ONLY' | 'IDEMPOTENT_WRITE' | 'HIGH_IMPACT'
  permissions: AgentCapabilityPermissions
  providerCompatibility: string[]
  attachment: AgentCapabilityAttachment
  diagnostics: string[]
}

export interface AgentCapabilityCatalog {
  schemaVersion: 'amesh.capability-catalog/v1'
  namespace: string | null
  generatedAt: string
  catalogDigest: string
  sourceAccess: Array<{ source: 'agents' | 'connections' | 'plugins'; status: 'allowed' | 'denied' | 'unavailable'; diagnostics: string[] }>
  total: number
  returned: number
  truncated: boolean
  items: AgentCapabilityCatalogItem[]
}

export type AgentResourceRef = components["schemas"]["AgentResourceRef"];
export type OrderedPromptRef = components["schemas"]["OrderedPromptRef"];
export type PromptSpec = components["schemas"]["PromptSpec"];

export type SkillSpec = components["schemas"]["SkillSpec"];

export type ModelRoute = Omit<components["schemas"]["ModelRoute"], 'provider' | 'parameters'> & {
  provider: {
    adapter: string
    endpoint: string
    embeddingEndpoint: string | null
    credentialRef: string
  }
  parameters: Record<string, unknown>
};
export type ModelPolicySpec = Omit<components["schemas"]["ModelPolicySpec"], 'routes'> & {
  routes: ModelRoute[]
};
export interface AgentEvaluationSpec {
  kind: 'EVALUATION'
  key: string
  namespace: string
  title: string
  description: string
  assertions: Array<Record<string, unknown>>
  rubric: Array<{
    key: string
    description: string
    assertion: Record<string, unknown>
    weight: string
  }>
  minimumRubricScore: string
  fixtures: Array<{
    key: string
    description: string
    input: Record<string, unknown>
    recordedOutput: Record<string, unknown>
  }>
  judge: {
    modelPolicy: AgentResourceRef
    prompt: string
    minimumScore: string
    maximumUncertainty: string
    maxCompletionTokens: number
  } | null
}

export interface AgentDefinitionSpec {
  kind: 'AGENT'
  key: string
  namespace: string
  title: string
  description: string
  instructions: string
  inputSchema: Record<string, unknown>
  outputSchema: Record<string, unknown>
  modelPolicy: AgentResourceRef
  prompts: OrderedPromptRef[]
  skills: AgentResourceRef[]
  tools: Array<{
    connectionKey: string
    connectionRevision: number
    toolName: string
    schemaDigest: string
  }>
  memoryPolicy: {
    scope: 'NONE' | 'EXECUTION' | 'PRIVATE' | 'SHARED'
    maxBytes: number
    retentionSeconds: number
    redact: boolean
    sharedScope: string | null
  }
  permissions: {
    delegatedCapabilities: string[]
    toolAllowlist: string[]
    secretScopes: string[]
    networkHosts: string[]
    filesystemReadRoots: string[]
    filesystemWriteRoots: string[]
    allowHighImpactTools: boolean
  }
  hardLimits: {
    maxTotalTokens: number
    maxCostUsd: string
    maxDurationSeconds: number
    maxToolCalls: number
    maxTurns: number
    maxLoopIterations: number
    maxRecursionDepth: number
    maxConcurrency: number
  }
  evaluationPolicy: {
    requiredEvaluations: string[]
    evaluations: AgentResourceRef[]
    requireHumanRelease: boolean
  }
}

export type AgentResourceSpec = PromptSpec | SkillSpec | ModelPolicySpec | AgentEvaluationSpec | AgentDefinitionSpec

export interface AgentResourceRevision {
  resourceId: string
  tenantId: string
  namespace: string
  kind: AgentResourceKind
  key: string
  revision: number
  digest: string
  spec: AgentResourceSpec
  createdBy: string
  createdAt: string
}

export interface AgentCapabilityPin {
  pinId: string
  tenantId: string
  namespace: string
  subjectRef: string
  envelopeDigest: string
  envelope: {
    schemaVersion: string
    agent: { key: string; revision: number; digest: string }
    resources: Array<{ kind: AgentResourceKind; key: string; revision: number; digest: string }>
    instructions: Array<{ sourceKind: string; sourceKey: string; order: number; content: string }>
    promptVariables: Record<string, string>
    modelRoutes: ModelRoute[]
    fallbackMode: string
    outputNondeterminismDisclosure: string
    tools: Array<Record<string, unknown>>
    inputSchema: Record<string, unknown>
    outputSchema: Record<string, unknown>
    memoryPolicy: AgentDefinitionSpec['memoryPolicy']
    permissions: AgentDefinitionSpec['permissions']
    hardLimits: AgentDefinitionSpec['hardLimits']
    evaluationPolicy: AgentDefinitionSpec['evaluationPolicy']
  }
  createdBy: string
  createdAt: string
}

export type AgentEnvelopePreview = Omit<components["schemas"]["AgentEnvelopePreview"], 'envelope'> & {
  envelope: AgentCapabilityPin['envelope']
}
export interface AgentSessionHarnessPin {
  adapter: string
  adapterVersion: string
  protocol: string
}

export type AgentSessionSummary = Omit<components["schemas"]["AgentSessionSummary"], 'counters' | 'contextReceipt' | 'finalResult' | 'error' | 'completedAt'> & {
  counters: {
    turns: number
    loopIterations: number
    toolCalls: number
    totalTokens: number
    costUsd: string
    repairAttempts: number
  }
  contextReceipt: Record<string, unknown> | null
  finalResult: Record<string, unknown> | null
  error: string | null
  completedAt: string | null
};
export type AgentSessionEvent = Omit<components["schemas"]["AgentSessionEvent"], 'eventId' | 'occurredAt' | 'payload'> & {
  eventId: string
  occurredAt: string
  payload: Record<string, unknown>
};
/** Safe, append-only progress projection shared by all run inspection views. */
export type AgentProgressActivity = components["schemas"]["AgentProgressActivity"];
export type AgentProgressStatus = components["schemas"]["AgentProgressStatus"];
export type AgentProgressFrame = components["schemas"]["AgentProgressFrame"];
export type AgentProgressEvent = components["schemas"]["AgentProgressEvent"];
export type AgentProgressPage = components["schemas"]["AgentProgressPage"];
export interface AgentProgressHeartbeat {
  type: 'heartbeat'
  sessionId: string
  cursor: string
}
export type AgentProgressStreamItem = AgentProgressEvent | AgentProgressHeartbeat

export interface AgentSessionDetailPage {
  session: AgentSessionSummary
  events: AgentSessionEvent[]
  nextEventIndex: number | null
}

export interface AgentSessionServiceDetailPage {
  session: AgentSessionControlSummary
  events: AgentSessionControlEvent[]
  nextEventIndex: number | null
}

/** Provider-neutral projection used by the session control room API. */
export type AgentSessionLifecycleState =
  | 'CREATED'
  | 'QUEUED'
  | 'RUNNING'
  | 'PAUSED'
  | 'CANCELLING'
  | 'CANCELLED'
  | 'SUCCEEDED'
  | 'FAILED'
  | 'WARNING'
  | 'RESTARTING'

export type AgentSessionHarnessCatalogEntry = components["schemas"]["AgentSessionHarnessCatalogEntry"];
export type AgentSessionHarnessCatalog = Record<string, AgentSessionHarnessCatalogEntry>

export interface AgentSessionBudgets {
  [key: string]: unknown
  maxTurns?: number
  maxToolCalls?: number
  maxTotalTokens?: number
  maxCostUsd?: string
}

export type AgentSessionControlSummary = Omit<components["schemas"]["AgentSessionControlSummary"], 'sessionId' | 'tenantId' | 'namespace' | 'executionId' | 'taskRunId' | 'attempt' | 'capabilityPinId' | 'envelopeDigest' | 'agentRef' | 'modelProfile' | 'harness' | 'version' | 'executionEpoch' | 'state' | 'phase' | 'createdAt' | 'updatedAt' | 'completedAt' | 'counters' | 'budgets' | 'result' | 'finalResult' | 'error'> & {
  sessionId: string
  tenantId?: string | null
  namespace?: string | null
  executionId?: string | null
  taskRunId?: string | null
  attempt?: number | null
  capabilityPinId?: string | null
  envelopeDigest?: string | null
  agentRef?: string | null
  modelProfile?: string | null
  harness?: AgentSessionHarnessPin | null
  version?: number | null
  executionEpoch?: number | null
  state: AgentSessionLifecycleState
  phase?: string | null
  createdAt: string
  updatedAt: string
  completedAt?: string | null
  counters?: Partial<AgentSessionSummary['counters']>
  budgets?: AgentSessionBudgets | null
  result?: Record<string, unknown> | null
  finalResult?: Record<string, unknown> | null
  error?: string | null
};
export interface AgentSessionControlEvent {
  eventId: string
  sessionId: string
  eventIndex: number
  eventKey: string
  eventType: string
  payload: Record<string, unknown>
  occurredAt: string
}

export interface AgentSessionControlEventPage {
  events: AgentSessionControlEvent[]
  nextEventIndex?: number | null
}

export type AgentSessionCreateRequest = Omit<components["schemas"]["AgentSessionCreateRequest"], 'agentRef' | 'businessAssertions' | 'dataHandling' | 'invalidOutputPolicy' | 'maxRepairAttempts' | 'memoryReadKeys' | 'runner' | 'timeoutMode'> & {
  agentRef: string
  input?: Record<string, unknown>
  businessAssertions?: Array<Record<string, unknown>>
  dataHandling?: components["schemas"]["ModelDataEgress"]
  invalidOutputPolicy?: 'FAIL' | 'REPAIR'
  maxRepairAttempts?: number | null
  memoryReadKeys?: string[]
  runner?: components["schemas"]["RunnerMode"]
  timeoutMode?: components["schemas"]["TaskTimeoutMode"]
};
export type AgentSessionLaunchResponse = components["schemas"]["AgentSessionLaunchResponse"];
export type AgentSessionServiceItem = Omit<components["schemas"]["AgentSessionServiceItem"], 'session'> & {
  session: AgentSessionControlSummary
}
export interface AgentSessionFleetQuery {
  limit?: number
  cursor?: string
  state?: AgentSessionLifecycleState
  namespace?: string
  agentRef?: string
  ownerId?: string
  harness?: string
  createdFrom?: string
  createdTo?: string
}

export type AgentSessionFleetItem = Omit<components["schemas"]["AgentSessionFleetItem"], 'state' | 'taskRunId' | 'counters'> & {
  state: AgentSessionLifecycleState
  taskRunId: string | null
  counters: AgentSessionSummary['counters']
};
export type AgentSessionFleetAggregates = components["schemas"]["AgentSessionFleetAggregates"];
export type AgentSessionFleetPage = Omit<components["schemas"]["AgentSessionFleetPage"], 'nextCursor' | 'items'> & {
  items: AgentSessionFleetItem[]
  nextCursor: string | null
};
export type AgentSessionInstanceTenantAggregate = components["schemas"]["AgentSessionInstanceTenantAggregate"];
export type AgentSessionInstanceAggregate = components["schemas"]["AgentSessionInstanceAggregate"];
export type AgentSessionPolicy = Omit<components["schemas"]["AgentSessionPolicy"], 'ceilingMode' | 'maxTotalTokens' | 'maxCostUsd' | 'maxDurationSeconds'> & {
  ceilingMode?: components["schemas"]["AgentCeilingMode"]
  maxTotalTokens: number
  maxCostUsd: string
  maxDurationSeconds: number
};
export interface AgentSessionPolicyDraft extends AgentSessionPolicy {
  namespace: string | null
  applicationId: string | null
  expectedRevision?: number
}

export type AgentSessionPolicyRevision = Omit<components["schemas"]["AgentSessionPolicyRevision"], 'policyId' | 'namespace' | 'applicationId' | 'spec'> & {
  policyId: string
  namespace: string | null
  applicationId: string | null
  spec: AgentSessionPolicy
};
export type AgentSessionAdminAction = 'cancel' | 'pause' | 'retry' | 'resume'

export interface AgentSessionAdminActionRequest {
  action: AgentSessionAdminAction
  items: Array<{ sessionId: string; expectedVersion: number; expectedEpoch: number }>
  reason: string
  confirmation: string
}

export interface AgentSessionAdminActionResult {
  action: AgentSessionAdminAction
  total: number
  applied: number
  rejected: number
  results: Array<{ sessionId: string; status: 'applied' | 'rejected'; execution?: Record<string, unknown> | null; error?: Record<string, unknown> | null }>
}

export type AgentSessionTransferMode = 'TERMINAL_HISTORY' | 'CLEAN_CHECKPOINT'

export interface AgentSessionProfileTransferBundle {
  schemaVersion: string
  sourceTenantId: string
  namespace: string
  agentKey: string
  agentRevision: number
  resources: unknown[]
  mcpConnections: unknown[]
  checksumSha256: string
}

export interface AgentSessionTransferBundle {
  schemaVersion: string
  mode: AgentSessionTransferMode
  sourceTenantId: string
  session: Record<string, unknown>
  checksumSha256: string
  capabilityPin?: Record<string, unknown> | null
  artifactDestinationRefs?: Record<string, string>
  [key: string]: unknown
}

export interface AgentSessionProfileCompatibilityReport {
  compatible: boolean
  targetTenantId: string
  targetNamespace: string
  resourcesToCreate: number
  resourcesExisting: number
  mcpConnectionsToCreate: number
  mcpConnectionsExisting: number
  issues: string[]
}

export interface AgentSessionCompatibilityReport {
  schemaVersion: string
  eligible: boolean
  mode: AgentSessionTransferMode
  sourceTenantId: string
  targetTenantId: string
  bundleDigest: string
  flowCompatible: boolean
  capabilityPinCompatible: boolean
  harnessCompatible: boolean
  credentialRebindingDiagnostics: string[]
  artifactDiagnostics: string[]
  issues: string[]
}

export interface AgentSessionProfileImportResult {
  targetTenantId: string
  targetNamespace: string
  agentKey: string
  agentRevision: number
  resourcesImported: number
  resourcesExisting: number
  mcpConnectionsImported: number
  mcpConnectionsExisting: number
  importId: string
  bundleDigest: string
  alreadyPresent: boolean
}

export interface AgentSessionImportResult {
  importId: string
  bundleDigest: string
  mode: AgentSessionTransferMode
  targetTenantId: string
  sessionId: string
  alreadyPresent: boolean
  idMapping: Record<string, string>
  credentialRebindingDiagnostics: string[]
}

export type AgentSessionControlRequest = components["schemas"]["AgentSessionControlRequest"];
export interface AgentSessionResult {
  sessionId: string
  state: AgentSessionLifecycleState
  result: Record<string, unknown> | null
  error: string | null
}

export type AgentRevisionComparison = components["schemas"]["AgentRevisionComparison"];
export interface AgentMcpConnectionRevision {
  connectionId: string
  tenantId: string
  revision: number
  digest: string
  spec: {
    key: string
    namespace: string
    endpoint: string
    credentialRef: string
    toolAllowlist: string[]
    tools: Array<AgentMcpToolPin>
  }
  createdBy: string
  createdAt: string
}

export interface AgentMcpToolPin {
  name: string
  description: string
  inputSchema: Record<string, unknown>
  outputSchema: Record<string, unknown> | null
  impact: 'READ_ONLY' | 'IDEMPOTENT_WRITE' | 'HIGH_IMPACT'
}

export interface AgentMcpDiscoveryResult {
  serverName: string
  serverVersion: string
  tools: AgentMcpToolPin[]
  digest: string
}

export interface AgentMcpConnectionSpec {
  key: string
  namespace: string
  endpoint: string
  credentialRef: string
  toolAllowlist: string[]
  tools: AgentMcpToolPin[]
}

export interface AgentMcpConnectionTestResult {
  status: 'PASSED' | 'SCHEMA_DRIFT' | 'UNAVAILABLE'
  evidenceId: string
  connectionPin: {
    key: string
    revision: number
    digest: string
  }
  observedDigest: string | null
  checkedToolCount: number
  diagnostic: string | null
  redacted: true
  effectBoundary: 'DISCOVERY_ONLY'
}

export interface AgentMcpToolCatalogEntry {
  connectionKey: string
  connectionRevision: number
  connectionDigest: string
  credentialRef: string
  endpoint: string
  toolName: string
  description: string
  schemaDigest: string
  impact: 'READ_ONLY' | 'IDEMPOTENT_WRITE' | 'HIGH_IMPACT'
}
