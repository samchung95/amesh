import type { components } from './generated/openapi'

export type CheckedOmit<T, K extends keyof T> = Omit<T, K>

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

export type UiSession = components["schemas"]["UiSessionResponse"];

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

export type AppFormField = components["schemas"]["FormField"];
export type AppFormSection = components["schemas"]["FormSection"];
export type AppForm = components["schemas"]["AppForm"];
export type WorkflowApp = components["schemas"]["WorkflowApp"];
export type HumanTaskState = components["schemas"]["HumanTaskState"];
export type HumanTaskActionKind = components["schemas"]["HumanTaskActionKind"];
export type HumanTaskAction = components["schemas"]["HumanTaskAction"];
export type HumanTask = components["schemas"]["HumanTask"];
export type HumanTaskNotification = components["schemas"]["HumanTaskNotification"];
export type AssetAccessMode = components["schemas"]["AssetAccessMode"];
export type AssetHealth = components["schemas"]["AssetHealth"];
export type AssetRegistrationSource = components["schemas"]["AssetRegistrationSource"];
export type LineageEvidenceKind = components["schemas"]["LineageEvidenceKind"];
export type AssetRecord = components["schemas"]["PersistedAsset"];
/** Editable asset input excludes persistence fields owned by the server. */
export type AssetDraft = CheckedOmit<AssetRecord, 'tenantId' | 'resourceVersion' | 'createdBy' | 'updatedBy' | 'createdAt' | 'updatedAt'>

export type AssetObservation = components["schemas"]["AssetObservation"];
export type AssetLineageEdge = components["schemas"]["AssetLineageEdge"];
export type AssetCatalogEntry = components["schemas"]["AssetCatalogEntry"];
export type DashboardDataSource = components["schemas"]["DashboardDataSource"];
export type DashboardVisualization = components["schemas"]["DashboardVisualization"];
export type DashboardAggregation = components["schemas"]["DashboardAggregation"];
export type DashboardMeasure = components["schemas"]["DashboardMeasure"];
export type DashboardFilters = components["schemas"]["DashboardFilters"];
export type DashboardQuery = components["schemas"]["DashboardQuery"];
export type DashboardWidget = components["schemas"]["DashboardWidget"];
export type DashboardDefinition = components["schemas"]["DashboardDefinition"];
export type DashboardSpec = components["schemas"]["DashboardSpec"];
export type DashboardQueryResult = components["schemas"]["DashboardQueryResult"];
export type DashboardRender = components["schemas"]["DashboardRender"];
export type SearchDocumentType = components["schemas"]["SearchDocumentType"];
export type SearchSortField = components["schemas"]["SearchSortField"];
export type SearchSortDirection = components["schemas"]["SearchSortDirection"];
export type SearchRangeField = components["schemas"]["SearchRangeField"];
export type SearchProjectionCondition = components["schemas"]["SearchProjectionCondition"];

export type SearchRange = components["schemas"]["SearchRange"];

export type SearchRequest = components["schemas"]["SearchRequest"];

export type SearchDocument = components["schemas"]["SearchDocument"];
export type SearchResponse = components["schemas"]["SearchResponse"];

export type SearchProjectionStatus = components["schemas"]["SearchProjectionStatus"];

export type SearchProjectionVerificationItem = components["schemas"]["SearchProjectionVerificationItem"];

export type SearchProjectionVerification = components["schemas"]["SearchProjectionVerification"];

export type PersistedFlow = components["schemas"]["PersistedFlow"];
export type SourcePosition = components["schemas"]["SourcePosition"];

export type FlowValidationIssue = components["schemas"]["ValidationIssue"];
export type FlowValidationResult = components["schemas"]["FlowValidationResult"];
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

export type FlowEditorSchema = components["schemas"]["FlowEditorSchemaResponse"];

export type FlowDocumentExport = components["schemas"]["FlowDocumentExport"];
export type FlowRevisionRecord = components["schemas"]["FlowRevisionRecord"];
export type FlowRevisionDiff = components["schemas"]["FlowRevisionDiff"];
export type FlowTestOutcome = components["schemas"]["FlowTestOutcome"];
export type FlowTestDefinitionDraft = components["schemas"]["FlowTestDefinitionCreateRequest"];

export type FlowTestDefinition = components["schemas"]["FlowTestDefinition"];
export type FlowTestCoverage = components["schemas"]["FlowTestCoverage"];
export type FlowTestAssertion = components["schemas"]["FlowTestAssertion"];
export type FlowTestCaseResult = components["schemas"]["FlowTestCaseResult"];
export type FlowTestRunResult = components["schemas"]["FlowTestRunResult"];
export type FlowTestQualityGate = components["schemas"]["FlowTestQualityGate"];
export type SimulationTaskPlan = components["schemas"]["SimulationTaskPlan"];

export type DeterminismPolicyPin = components["schemas"]["DeterminismPolicyPin"];
export type DeterminismNode = components["schemas"]["DeterminismNode"];
export type DynamicExecutionBound = components["schemas"]["DynamicExecutionBound"];
export type DeterminismEnvelope = components["schemas"]["DeterminismEnvelope"];
export type SimulationPlan = components["schemas"]["SimulationPlan"];
export type FlowFormatResponse = components["schemas"]["FlowFormatResponse"];
export type ExpressionPreviewResponse = components["schemas"]["ExpressionPreviewResponse"];
export type BlueprintCatalogSource = components["schemas"]["BlueprintCatalogSource"];
export type BlueprintParameter = components["schemas"]["BlueprintParameter"];
export type BlueprintProvenance = components["schemas"]["BlueprintProvenance"];
export type BlueprintSummary = components["schemas"]["BlueprintSummary"];
export type BlueprintDefinition = components["schemas"]["BlueprintDefinition"];
export type BlueprintDraftResponse = components["schemas"]["BlueprintDraftResponse"];
export type PlaygroundSimulationResponse = components["schemas"]["PlaygroundSimulationResponse"];
export type ExecutionState = components["schemas"]["ExecutionState"];
export type ExecutionRunner = 'local' | 'docker' | 'kubernetes'

export type PersistedExecution = components["schemas"]["PersistedExecution"];
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

export type FlowDataContract = components["schemas"]["FlowDataContract"];
export type FlowMetadata = components["schemas"]["FlowMetadataResponse"];

export type PersistedTaskRun = components["schemas"]["PersistedTaskRun"];
export type ExecutionDetail = components["schemas"]["ExecutionDetail"];
export type TaskRunSummary = components["schemas"]["PersistedTaskRunSummary"];

export type ExecutionEvidenceKind = components["schemas"]["ExecutionEvidenceKind"];
export type ExecutionEvidenceEvent = components["schemas"]["ExecutionEvidenceEvent"];
export type ExecutionEvidencePage = components["schemas"]["ExecutionEvidencePage"];
export interface ExecutionEvidenceStreamEvent extends ExecutionEvidenceEvent {
  nextCursor: string
}

export type ExecutionInterventionAction = components["schemas"]["ExecutionInterventionAction"];
export type ExecutionInterventionPreview = components["schemas"]["ExecutionInterventionPreview"];
export type ExecutionInterventionRecord = components["schemas"]["ExecutionInterventionRecord"];
export type PersistedSubflow = components["schemas"]["PersistedSubflow"];
export type ExecutionArtifact = components["schemas"]["ExecutionArtifact"];
export type BackfillSpec = components["schemas"]["BackfillSpec"];
export type BackfillPreview = components["schemas"]["BackfillPreview"];
export type BackfillRecord = components["schemas"]["BackfillRecord"];
export type TriggerOccurrenceState = components["schemas"]["TriggerOccurrenceState"];

export type TriggerRuntimeState = components["schemas"]["TriggerRuntimeState"];

export type TriggerOccurrence = components["schemas"]["TriggerOccurrence"];

export type CheckOutcome = components["schemas"]["CheckOutcome"];
export type CheckEvaluation = components["schemas"]["CheckEvaluation"];
export type CheckComplianceSummary = components["schemas"]["CheckComplianceSummary"];
export type NamespaceCheckPolicy = components["schemas"]["NamespaceCheckPolicy"];
export type FlowGraphNode = components["schemas"]["FlowGraphNode"];
export type FlowGraphEdge = components["schemas"]["FlowGraphEdge"];
export type FlowGraph = components["schemas"]["FlowGraph"];
export type HealthResponse = components["schemas"]["HealthResponse"];
export type ReadinessResponse = components["schemas"]["ReadinessResponse"];
export type PrincipalDefinition = components["schemas"]["PrincipalDefinition"];

export type PermissionDefinition = components["schemas"]["Permission"];

export type RoleDefinition = components["schemas"]["RoleDefinition"];

export type RoleBinding = components["schemas"]["RoleBinding"];

export type CredentialMetadata = components["schemas"]["CredentialMetadata"];
export type IssuedCredential = components["schemas"]["IssuedCredentialResponse"];

export type NamespaceWorkflowMetadataView = components["schemas"]["NamespaceWorkflowMetadataView"];
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
export type Announcement = components["schemas"]["Announcement"];
export type AnnouncementDraft = components["schemas"]["AnnouncementCreateRequest"];

export type OperationalBoundary = components["schemas"]["OperationalBoundary"];
export type OperationalControlScope = components["schemas"]["OperationalControlScope"];
export type RunningWorkPolicy = components["schemas"]["RunningWorkPolicy"];

export type OperationalControlAcknowledgement = components["schemas"]["OperationalControlAcknowledgement"];
export type OperationalControl = components["schemas"]["OperationalControl"];
export type OperationalControlDraft = components["schemas"]["OperationalControlCreateRequest"];

export type OperationalControlAction = components["schemas"]["OperationalControlActionRequest"];

export type OperationalControlEvent = components["schemas"]["OperationalControlEvent"];
export type AuthenticationProvider = components["schemas"]["AuthenticationProviderDescriptor"];

export type LoginResponse = components["schemas"]["LoginResponse"];
export type NamespaceFile = components["schemas"]["NamespaceFile"];
export type NamespaceResourceBundle = components["schemas"]["NamespaceResourceBundle"];
export type ImageArtifactRef = components["schemas"]["ImageArtifactRef"];
export type NamespaceFileVersion = components["schemas"]["NamespaceFileVersion"];
export type ArtifactRef = components["schemas"]["ArtifactRef"];
export type KeyValueType = components["schemas"]["KeyValueType"];
export type KeyValueEntry = components["schemas"]["KeyValueEntry"];
export type SecretBinding = components["schemas"]["SecretBinding"];

export type PluginRegistryAttachmentKind = components["schemas"]["PluginRegistryAttachmentKind"];

export type PluginRegistryPackage = components["schemas"]["PluginRegistryPackage"];
export type PluginRegistryIndex = components["schemas"]["PluginRegistryIndex"];

export type PluginPolicyScope = components["schemas"]["PluginPolicyScope"];
export type PluginPolicyStage = components["schemas"]["PluginPolicyStage"];

export type PluginPolicyRuleDraft = components["schemas"]["PluginPolicyRuleCreate"];

export type PluginPolicyRule = components["schemas"]["PluginPolicyRule"];

export type PluginQuarantineDraft = components["schemas"]["PluginQuarantineCreate"];

export type PluginQuarantine = components["schemas"]["PluginQuarantine"];

export type EffectivePluginPolicy = components["schemas"]["EffectivePluginPolicy"];
export type PluginPolicyImpactPreview = components["schemas"]["PluginPolicyImpactPreview"];

export type AdmissionPolicyStage = components["schemas"]["PolicyStage"];
export type AdmissionPolicyOutcome = components["schemas"]["PolicyOutcome"];
export type AdmissionPolicyOperator = components["schemas"]["PolicyOperator"];

export type AdmissionPolicyDocument = components["schemas"]["PolicyDocument"];

export type AdmissionPolicyRevision = components["schemas"]["PolicyRevision"];

export type AdmissionPolicyDecision = components["schemas"]["PolicyDecision"];

export type LifecycleResourceType = components["schemas"]["LifecycleResourceType"];
export type LifecycleScope = components["schemas"]["LifecycleScope"];
export type LifecyclePolicyDraft = components["schemas"]["LifecyclePolicyDraft"];
export type LifecyclePolicy = components["schemas"]["LifecyclePolicy"];
export type LifecycleLegalHoldDraft = components["schemas"]["LifecycleLegalHoldDraft"];
export type LifecycleLegalHold = components["schemas"]["LifecycleLegalHold"];
export type LifecycleJob = components["schemas"]["LifecycleJob"];
export type UpgradeRelease = components["schemas"]["UpgradeRelease"];
export type UpgradePath = components["schemas"]["UpgradePath"];
export type UpgradePolicy = components["schemas"]["UpgradePolicy"];
export type UpgradeCheck = components["schemas"]["UpgradeCheck"];
export type UpgradeReport = components["schemas"]["UpgradeReport"];
export type PersistedEventMigration = components["schemas"]["PersistedEventMigration"];
export type AgentResourceKind = components["schemas"]["AgentResourceKind"];
export type AgentCapabilityKind = components["schemas"]["CapabilityKind"];
export type AgentCapabilityStatus = components["schemas"]["CapabilityStatus"];

export type AgentCapabilityPermissions = components["schemas"]["CapabilityPermissions"];

export type AgentCapabilityReference = components["schemas"]["CapabilityReference"];

export type AgentCapabilityAttachment = components["schemas"]["CapabilityAttachment"];

export type AgentCapabilityCatalogItem = components["schemas"]["CapabilityCatalogItem"];

export type AgentCapabilityCatalog = components["schemas"]["CapabilityCatalog"];

export type AgentResourceRef = components["schemas"]["AgentResourceRef"];
export type OrderedPromptRef = components["schemas"]["OrderedPromptRef"];
export type PromptSpec = components["schemas"]["PromptSpec"];

export type SkillSpec = components["schemas"]["SkillSpec"];

export type ModelRoute = components["schemas"]["ModelRoute"];
export type ModelPolicySpec = components["schemas"]["ModelPolicySpec"];
export type AgentEvaluationSpec = components["schemas"]["AgentEvaluationSpec-Input"];

export type AgentDefinitionSpec = components["schemas"]["AgentDefinitionSpec-Input"];

export type AgentResourceSpec = PromptSpec | SkillSpec | ModelPolicySpec | AgentEvaluationSpec | AgentDefinitionSpec

export type AgentResourceRevision = components["schemas"]["AgentResourceRevision-Output"];

export type AgentCapabilityPin = components["schemas"]["AgentCapabilityPin-Output"];

export type AgentEnvelopePreview = components["schemas"]["AgentEnvelopePreview"];
export type AgentSessionHarnessPin = components["schemas"]["AgentHarnessPin"];

export type AgentSessionSummary = components["schemas"]["AgentSessionSummary"];
export type AgentSessionEvent = components["schemas"]["AgentSessionEvent"];
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

export type AgentSessionDetailPage = components["schemas"]["AgentSessionDetailResponse"];

export type AgentSessionServiceDetailPage = components["schemas"]["AgentSessionServiceDetailResponse"];

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

export type AgentSessionControlSummary = components["schemas"]["AgentSessionControlSummary"];
export type AgentSessionControlEvent = components["schemas"]["AgentSessionEvent"];

export interface AgentSessionControlEventPage {
  events: AgentSessionControlEvent[]
  nextEventIndex?: number | null
}

export type AgentSessionCreateRequest = components["schemas"]["AgentSessionCreateRequest"];
/** The UI requires an explicit agent even though the wire request permits server-side resolution. */
export type AgentSessionCreateDraft = CheckedOmit<Partial<AgentSessionCreateRequest>, 'agentRef'> & {
  agentRef: string
}
export type AgentSessionLaunchResponse = components["schemas"]["AgentSessionLaunchResponse"];
export type AgentSessionServiceItem = components["schemas"]["AgentSessionServiceItem"];
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

export type AgentSessionFleetItem = components["schemas"]["AgentSessionFleetItem"];
export type AgentSessionFleetAggregates = components["schemas"]["AgentSessionFleetAggregates"];
export type AgentSessionFleetPage = components["schemas"]["AgentSessionFleetPage"];
export type AgentSessionInstanceTenantAggregate = components["schemas"]["AgentSessionInstanceTenantAggregate"];
export type AgentSessionInstanceAggregate = components["schemas"]["AgentSessionInstanceAggregate"];
export type AgentSessionPolicy = components["schemas"]["AgentSessionPolicy"];
/** The policy editor requires finite limits while the wire policy permits unbounded nulls. */
export type AgentSessionPolicyDraft = CheckedOmit<AgentSessionPolicy, 'ceilingMode' | 'maxTotalTokens' | 'maxCostUsd' | 'maxDurationSeconds'> & {
  namespace: string | null
  applicationId: string | null
  ceilingMode?: AgentSessionPolicy['ceilingMode']
  maxTotalTokens: number
  maxCostUsd: string
  maxDurationSeconds: number
  expectedRevision?: number
}

export type AgentSessionPolicyRevision = components["schemas"]["AgentSessionPolicyRevision"];
export type AgentSessionAdminAction = 'cancel' | 'pause' | 'retry' | 'resume'

export type AgentSessionAdminActionRequest = components["schemas"]["AgentSessionBulkActionRequest"];

export type AgentSessionAdminActionResult = components["schemas"]["AgentSessionBulkActionResponse"];

export type AgentSessionTransferMode = components["schemas"]["SessionTransferMode"];
export type AgentSessionProfileTransferBundle = components["schemas"]["ProfileBundle-Input"];
export type AgentSessionTransferBundle = components["schemas"]["SessionTransferBundle-Input"];

export type AgentSessionProfileCompatibilityReport = components["schemas"]["ProfileCompatibilityReport"];

export type AgentSessionCompatibilityReport = components["schemas"]["SessionTransferCompatibilityReport"];

export type AgentSessionProfileImportResult = components["schemas"]["ProfileImportResult"];

export type AgentSessionImportResult = components["schemas"]["SessionTransferImportResult"];

export type AgentSessionControlRequest = components["schemas"]["AgentSessionControlRequest"];
export type AgentSessionResult = components["schemas"]["AgentSessionResultResponse"];

export type AgentRevisionComparison = components["schemas"]["AgentRevisionComparison"];
export type AgentMcpConnectionRevision = components["schemas"]["McpConnectionRevision"];

export type AgentMcpToolPin = components["schemas"]["McpToolPin"];

export type AgentMcpDiscoveryResult = components["schemas"]["McpDiscoveryResult"];

export type AgentMcpConnectionSpec = components["schemas"]["McpConnectionSpec"];

export type AgentMcpConnectionTestResult = components["schemas"]["McpConnectionTestResponse"];

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

type IsExact<Left, Right> =
  (<Value>() => Value extends Left ? 1 : 2) extends
  (<Value>() => Value extends Right ? 1 : 2)
    ? (<Value>() => Value extends Right ? 1 : 2) extends
      (<Value>() => Value extends Left ? 1 : 2)
      ? true
      : false
    : false
type AssertExact<Comparison extends true> = Comparison

/** Compile-time proof that compatibility names remain exact generated wire aliases. */
export type GeneratedCompatibilityContracts = [
  AssertExact<IsExact<UiSession, components["schemas"]["UiSessionResponse"]>>,
  AssertExact<IsExact<AssetRecord, components["schemas"]["PersistedAsset"]>>,
  AssertExact<IsExact<AppFormField, components["schemas"]["FormField"]>>,
  AssertExact<IsExact<AppFormSection, components["schemas"]["FormSection"]>>,
  AssertExact<IsExact<AppForm, components["schemas"]["AppForm"]>>,
  AssertExact<IsExact<WorkflowApp, components["schemas"]["WorkflowApp"]>>,
  AssertExact<IsExact<HumanTask, components["schemas"]["HumanTask"]>>,
  AssertExact<IsExact<DashboardFilters, components["schemas"]["DashboardFilters"]>>,
  AssertExact<IsExact<DashboardQuery, components["schemas"]["DashboardQuery"]>>,
  AssertExact<IsExact<DashboardWidget, components["schemas"]["DashboardWidget"]>>,
  AssertExact<IsExact<DashboardDefinition, components["schemas"]["DashboardDefinition"]>>,
  AssertExact<IsExact<DashboardSpec, components["schemas"]["DashboardSpec"]>>,
  AssertExact<IsExact<DashboardRender, components["schemas"]["DashboardRender"]>>,
  AssertExact<IsExact<SearchDocument, components["schemas"]["SearchDocument"]>>,
  AssertExact<IsExact<SearchResponse, components["schemas"]["SearchResponse"]>>,
  AssertExact<IsExact<SearchRequest, components["schemas"]["SearchRequest"]>>,
  AssertExact<IsExact<FlowValidationIssue, components["schemas"]["ValidationIssue"]>>,
  AssertExact<IsExact<FlowValidationResult, components["schemas"]["FlowValidationResult"]>>,
  AssertExact<IsExact<FlowTestDefinitionDraft, components["schemas"]["FlowTestDefinitionCreateRequest"]>>,
  AssertExact<IsExact<DeterminismPolicyPin, components["schemas"]["DeterminismPolicyPin"]>>,
  AssertExact<IsExact<DeterminismEnvelope, components["schemas"]["DeterminismEnvelope"]>>,
  AssertExact<IsExact<SimulationPlan, components["schemas"]["SimulationPlan"]>>,
  AssertExact<IsExact<FlowFormatResponse, components["schemas"]["FlowFormatResponse"]>>,
  AssertExact<IsExact<PlaygroundSimulationResponse, components["schemas"]["PlaygroundSimulationResponse"]>>,
  AssertExact<IsExact<PersistedExecution, components["schemas"]["PersistedExecution"]>>,
  AssertExact<IsExact<FlowDataContract, components["schemas"]["FlowDataContract"]>>,
  AssertExact<IsExact<PersistedTaskRun, components["schemas"]["PersistedTaskRun"]>>,
  AssertExact<IsExact<ExecutionDetail, components["schemas"]["ExecutionDetail"]>>,
  AssertExact<IsExact<TaskRunSummary, components["schemas"]["PersistedTaskRunSummary"]>>,
  AssertExact<IsExact<ExecutionEvidenceEvent, components["schemas"]["ExecutionEvidenceEvent"]>>,
  AssertExact<IsExact<ExecutionEvidencePage, components["schemas"]["ExecutionEvidencePage"]>>,
  AssertExact<IsExact<ExecutionInterventionPreview, components["schemas"]["ExecutionInterventionPreview"]>>,
  AssertExact<IsExact<PersistedSubflow, components["schemas"]["PersistedSubflow"]>>,
  AssertExact<IsExact<BackfillSpec, components["schemas"]["BackfillSpec"]>>,
  AssertExact<IsExact<TriggerOccurrence, components["schemas"]["TriggerOccurrence"]>>,
  AssertExact<IsExact<ReadinessResponse, components["schemas"]["ReadinessResponse"]>>,
  AssertExact<IsExact<PrincipalDefinition, components["schemas"]["PrincipalDefinition"]>>,
  AssertExact<IsExact<RoleBinding, components["schemas"]["RoleBinding"]>>,
  AssertExact<IsExact<NamespaceWorkflowMetadataView, components["schemas"]["NamespaceWorkflowMetadataView"]>>,
  AssertExact<IsExact<Announcement, components["schemas"]["Announcement"]>>,
  AssertExact<IsExact<OperationalControl, components["schemas"]["OperationalControl"]>>,
  AssertExact<IsExact<NamespaceResourceBundle, components["schemas"]["NamespaceResourceBundle"]>>,
  AssertExact<IsExact<ImageArtifactRef, components["schemas"]["ImageArtifactRef"]>>,
  AssertExact<IsExact<PluginRegistryPackage, components["schemas"]["PluginRegistryPackage"]>>,
  AssertExact<IsExact<PluginRegistryIndex, components["schemas"]["PluginRegistryIndex"]>>,
  AssertExact<IsExact<PluginPolicyRule, components["schemas"]["PluginPolicyRule"]>>,
  AssertExact<IsExact<EffectivePluginPolicy, components["schemas"]["EffectivePluginPolicy"]>>,
  AssertExact<IsExact<LifecyclePolicyDraft, components["schemas"]["LifecyclePolicyDraft"]>>,
  AssertExact<IsExact<LifecyclePolicy, components["schemas"]["LifecyclePolicy"]>>,
  AssertExact<IsExact<LifecycleJob, components["schemas"]["LifecycleJob"]>>,
  AssertExact<IsExact<ModelRoute, components["schemas"]["ModelRoute"]>>,
  AssertExact<IsExact<ModelPolicySpec, components["schemas"]["ModelPolicySpec"]>>,
  AssertExact<IsExact<AgentEnvelopePreview, components["schemas"]["AgentEnvelopePreview"]>>,
  AssertExact<IsExact<AgentSessionSummary, components["schemas"]["AgentSessionSummary"]>>,
  AssertExact<IsExact<AgentSessionEvent, components["schemas"]["AgentSessionEvent"]>>,
  AssertExact<IsExact<AgentSessionControlSummary, components["schemas"]["AgentSessionControlSummary"]>>,
  AssertExact<IsExact<AgentSessionCreateRequest, components["schemas"]["AgentSessionCreateRequest"]>>,
  AssertExact<IsExact<AgentSessionServiceItem, components["schemas"]["AgentSessionServiceItem"]>>,
  AssertExact<IsExact<AgentSessionFleetItem, components["schemas"]["AgentSessionFleetItem"]>>,
  AssertExact<IsExact<AgentSessionFleetPage, components["schemas"]["AgentSessionFleetPage"]>>,
  AssertExact<IsExact<AgentSessionPolicy, components["schemas"]["AgentSessionPolicy"]>>,
  AssertExact<IsExact<AgentSessionPolicyRevision, components["schemas"]["AgentSessionPolicyRevision"]>>,
  AssertExact<IsExact<AgentSessionTransferMode, components["schemas"]["SessionTransferMode"]>>,
  AssertExact<IsExact<AgentSessionProfileTransferBundle, components["schemas"]["ProfileBundle-Input"]>>,
  AssertExact<IsExact<AgentSessionTransferBundle, components["schemas"]["SessionTransferBundle-Input"]>>,
  AssertExact<IsExact<AgentSessionImportResult, components["schemas"]["SessionTransferImportResult"]>>,
  AssertExact<IsExact<FlowEditorSchema, components["schemas"]["FlowEditorSchemaResponse"]>>,
  AssertExact<IsExact<FlowMetadata, components["schemas"]["FlowMetadataResponse"]>>,
  AssertExact<IsExact<PermissionDefinition, components["schemas"]["Permission"]>>,
  AssertExact<IsExact<IssuedCredential, components["schemas"]["IssuedCredentialResponse"]>>,
  AssertExact<IsExact<AnnouncementDraft, components["schemas"]["AnnouncementCreateRequest"]>>,
  AssertExact<IsExact<OperationalControlDraft, components["schemas"]["OperationalControlCreateRequest"]>>,
  AssertExact<IsExact<OperationalControlAction, components["schemas"]["OperationalControlActionRequest"]>>,
  AssertExact<IsExact<AuthenticationProvider, components["schemas"]["AuthenticationProviderDescriptor"]>>,
  AssertExact<IsExact<PluginPolicyRuleDraft, components["schemas"]["PluginPolicyRuleCreate"]>>,
  AssertExact<IsExact<PluginQuarantineDraft, components["schemas"]["PluginQuarantineCreate"]>>,
  AssertExact<IsExact<AdmissionPolicyStage, components["schemas"]["PolicyStage"]>>,
  AssertExact<IsExact<AdmissionPolicyOutcome, components["schemas"]["PolicyOutcome"]>>,
  AssertExact<IsExact<AdmissionPolicyOperator, components["schemas"]["PolicyOperator"]>>,
  AssertExact<IsExact<AdmissionPolicyDocument, components["schemas"]["PolicyDocument"]>>,
  AssertExact<IsExact<AdmissionPolicyRevision, components["schemas"]["PolicyRevision"]>>,
  AssertExact<IsExact<AdmissionPolicyDecision, components["schemas"]["PolicyDecision"]>>,
  AssertExact<IsExact<AgentCapabilityKind, components["schemas"]["CapabilityKind"]>>,
  AssertExact<IsExact<AgentCapabilityStatus, components["schemas"]["CapabilityStatus"]>>,
  AssertExact<IsExact<AgentCapabilityPermissions, components["schemas"]["CapabilityPermissions"]>>,
  AssertExact<IsExact<AgentCapabilityReference, components["schemas"]["CapabilityReference"]>>,
  AssertExact<IsExact<AgentCapabilityAttachment, components["schemas"]["CapabilityAttachment"]>>,
  AssertExact<IsExact<AgentCapabilityCatalogItem, components["schemas"]["CapabilityCatalogItem"]>>,
  AssertExact<IsExact<AgentCapabilityCatalog, components["schemas"]["CapabilityCatalog"]>>,
  AssertExact<IsExact<AgentEvaluationSpec, components["schemas"]["AgentEvaluationSpec-Input"]>>,
  AssertExact<IsExact<AgentDefinitionSpec, components["schemas"]["AgentDefinitionSpec-Input"]>>,
  AssertExact<IsExact<AgentResourceRevision, components["schemas"]["AgentResourceRevision-Output"]>>,
  AssertExact<IsExact<AgentCapabilityPin, components["schemas"]["AgentCapabilityPin-Output"]>>,
  AssertExact<IsExact<AgentSessionHarnessPin, components["schemas"]["AgentHarnessPin"]>>,
  AssertExact<IsExact<AgentSessionDetailPage, components["schemas"]["AgentSessionDetailResponse"]>>,
  AssertExact<IsExact<AgentSessionServiceDetailPage, components["schemas"]["AgentSessionServiceDetailResponse"]>>,
  AssertExact<IsExact<AgentSessionControlEvent, components["schemas"]["AgentSessionEvent"]>>,
  AssertExact<IsExact<AgentSessionAdminActionRequest, components["schemas"]["AgentSessionBulkActionRequest"]>>,
  AssertExact<IsExact<AgentSessionAdminActionResult, components["schemas"]["AgentSessionBulkActionResponse"]>>,
  AssertExact<IsExact<AgentSessionProfileCompatibilityReport, components["schemas"]["ProfileCompatibilityReport"]>>,
  AssertExact<IsExact<AgentSessionCompatibilityReport, components["schemas"]["SessionTransferCompatibilityReport"]>>,
  AssertExact<IsExact<AgentSessionProfileImportResult, components["schemas"]["ProfileImportResult"]>>,
  AssertExact<IsExact<AgentSessionResult, components["schemas"]["AgentSessionResultResponse"]>>,
  AssertExact<IsExact<AgentMcpConnectionRevision, components["schemas"]["McpConnectionRevision"]>>,
  AssertExact<IsExact<AgentMcpToolPin, components["schemas"]["McpToolPin"]>>,
  AssertExact<IsExact<AgentMcpDiscoveryResult, components["schemas"]["McpDiscoveryResult"]>>,
  AssertExact<IsExact<AgentMcpConnectionSpec, components["schemas"]["McpConnectionSpec"]>>,
  AssertExact<IsExact<AgentMcpConnectionTestResult, components["schemas"]["McpConnectionTestResponse"]>>,
]
