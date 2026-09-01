import type {
  AgentMcpToolCatalogEntry,
  AgentResourceRevision,
  AgentResourceSpec,
  AgentResourceKind,
} from '../api/types'

export const agentKinds: Array<{ value: AgentResourceKind; label: string; description: string }> = [
  { value: 'PROMPT', label: 'Prompt', description: 'Reusable instruction content with immutable revisions.' },
  { value: 'SKILL', label: 'Skill', description: 'Declarative operating guidance and requested capabilities.' },
  { value: 'MODEL_POLICY', label: 'Model policy', description: 'Provider routes, model choice, and explicit fallback behavior.' },
  { value: 'EVALUATION', label: 'Evaluation', description: 'Versioned deterministic assertions, fixtures, and optional judge policy.' },
  { value: 'AGENT', label: 'Agent', description: 'The complete capability envelope boundary.' },
]

export const DEFAULT_OPENROUTER_MODEL = 'openai/gpt-5.6-luna'

export const openRouterModels: Array<{
  value: string
  label: string
  description: string
  requiredFeatures: string[]
}> = [
  {
    value: DEFAULT_OPENROUTER_MODEL,
    label: 'GPT-5.6 Luna · default',
    description: 'Project base model through OpenRouter.',
    requiredFeatures: ['structured-output'],
  },
  {
    value: 'openai/gpt-5.6-terra',
    label: 'GPT-5.6 Terra',
    description: 'OpenAI Terra through OpenRouter.',
    requiredFeatures: ['structured-output'],
  },
  {
    value: 'openai/gpt-5.6-sol',
    label: 'GPT-5.6 Sol',
    description: 'OpenAI Sol through OpenRouter.',
    requiredFeatures: ['structured-output'],
  },
  {
    value: 'deepseek/deepseek-v4-flash-vision-exp',
    label: 'DeepSeek V4 Flash Vision · experimental',
    description: 'Vision-capable DeepSeek V4 Flash through OpenRouter.',
    requiredFeatures: ['structured-output', 'image-input'],
  },
]

export const schemaPresets = {
  object: { type: 'object', additionalProperties: true },
  question: {
    type: 'object',
    properties: { question: { type: 'string' } },
    required: ['question'],
    additionalProperties: false,
  },
  structuredAnswer: {
    type: 'object',
    properties: {
      answer: { type: 'string' },
      confidence: { type: 'number', minimum: 0, maximum: 1 },
    },
    required: ['answer'],
    additionalProperties: false,
  },
} as const

export interface AgentBuilderDraft {
  kind: AgentResourceKind
  key: string
  title: string
  description: string
  instructions: string
  model: string
  credentialRef: string
  requestedCapability: string
  modelPolicyRef: string
  promptRef: string
  skillRef: string
  toolRef: string
  evaluationRef: string
  inputPreset: keyof typeof schemaPresets
  outputPreset: keyof typeof schemaPresets
  memoryScope: 'NONE' | 'EXECUTION' | 'PRIVATE' | 'SHARED'
  sharedScope: string
  requireHumanRelease: boolean
  maxTotalTokens: number
  maxCostUsd: string
  maxDurationSeconds: number
  maxToolCalls: number
  maxTurns: number
}

export const initialAgentBuilderDraft: AgentBuilderDraft = {
  kind: 'AGENT',
  key: '',
  title: '',
  description: '',
  instructions: '',
  model: DEFAULT_OPENROUTER_MODEL,
  credentialRef: 'openrouter-api-key',
  requestedCapability: 'cite',
  modelPolicyRef: '',
  promptRef: '',
  skillRef: '',
  toolRef: '',
  evaluationRef: '',
  inputPreset: 'question',
  outputPreset: 'structuredAnswer',
  memoryScope: 'NONE',
  sharedScope: '',
  requireHumanRelease: false,
  maxTotalTokens: 4_000,
  maxCostUsd: '0.20',
  maxDurationSeconds: 120,
  maxToolCalls: 4,
  maxTurns: 3,
}

export function revisionRef(resource: AgentResourceRevision): string {
  return `${resource.key}@${String(resource.revision)}`
}

function selectedResource(
  resources: AgentResourceRevision[],
  ref: string,
  kind: AgentResourceKind,
): AgentResourceRevision | undefined {
  return resources.find((resource) => resource.kind === kind && revisionRef(resource) === ref)
}

function endpointHost(endpoint: string): string {
  return new URL(endpoint).hostname
}

export function buildAgentResourceSpec(
  namespace: string,
  draft: AgentBuilderDraft,
  resources: AgentResourceRevision[],
  tools: AgentMcpToolCatalogEntry[],
): AgentResourceSpec {
  const shared = { key: draft.key.trim(), namespace, title: draft.title.trim() }
  if (draft.kind === 'PROMPT') {
    return { kind: 'PROMPT', ...shared, content: draft.instructions.trim(), variables: {} }
  }
  if (draft.kind === 'SKILL') {
    return {
      kind: 'SKILL',
      ...shared,
      description: draft.description.trim(),
      instructions: draft.instructions.trim(),
      requestedCapabilities: draft.requestedCapability ? [draft.requestedCapability] : [],
    }
  }
  if (draft.kind === 'MODEL_POLICY') {
    const requiredFeatures = openRouterModels.find((model) => model.value === draft.model)?.requiredFeatures
      ?? ['structured-output']
    return {
      kind: 'MODEL_POLICY',
      ...shared,
      routes: [{
        routeId: 'primary',
        provider: {
          adapter: 'openai-compatible',
          endpoint: 'https://openrouter.ai/api/v1',
          embeddingEndpoint: null,
          credentialRef: draft.credentialRef,
        },
        model: draft.model,
        requiredFeatures: [...requiredFeatures],
        parameters: {},
      }],
      fallbackMode: 'DISABLED',
      outputNondeterminismDisclosure: 'Model output is nondeterministic; durable behavior is defined by pinned schemas, limits, and capability revisions.',
    }
  }
  if (draft.kind === 'EVALUATION') {
    const judgePolicy = selectedResource(resources, draft.modelPolicyRef, 'MODEL_POLICY')
    return {
      kind: 'EVALUATION',
      ...shared,
      description: draft.description.trim(),
      assertions: [schemaPresets.structuredAnswer],
      rubric: [],
      minimumRubricScore: '1',
      fixtures: [],
      judge: judgePolicy ? {
        modelPolicy: { key: judgePolicy.key, revision: judgePolicy.revision },
        prompt: 'Score the candidate output against the pinned rubric. Report uncertainty honestly.',
        minimumScore: '0.8',
        maximumUncertainty: '0.2',
        maxCompletionTokens: 500,
      } : null,
    }
  }

  const modelPolicy = selectedResource(resources, draft.modelPolicyRef, 'MODEL_POLICY')
  if (!modelPolicy || modelPolicy.spec.kind !== 'MODEL_POLICY') {
    throw new Error('Choose an exact model-policy revision.')
  }
  const prompt = selectedResource(resources, draft.promptRef, 'PROMPT')
  const skill = selectedResource(resources, draft.skillRef, 'SKILL')
  const tool = tools.find((item) => `${item.connectionKey}@${String(item.connectionRevision)}:${item.toolName}` === draft.toolRef)
  const evaluation = selectedResource(resources, draft.evaluationRef, 'EVALUATION')
  const evaluationJudgePolicy = evaluation?.spec.kind === 'EVALUATION' && evaluation.spec.judge
    ? selectedResource(resources, `${evaluation.spec.judge.modelPolicy.key}@${String(evaluation.spec.judge.modelPolicy.revision)}`, 'MODEL_POLICY')
    : undefined
  const delegatedCapabilities = skill?.spec.kind === 'SKILL'
    ? skill.spec.requestedCapabilities
    : []
  const secretScopes = [
    ...modelPolicy.spec.routes.map((route) => route.provider.credentialRef),
    ...(evaluationJudgePolicy?.spec.kind === 'MODEL_POLICY' ? evaluationJudgePolicy.spec.routes.map((route) => route.provider.credentialRef) : []),
    ...(tool ? [tool.credentialRef] : []),
  ].filter((value, index, values) => values.indexOf(value) === index)
  const networkHosts = [
    ...modelPolicy.spec.routes.map((route) => endpointHost(route.provider.endpoint)),
    ...(evaluationJudgePolicy?.spec.kind === 'MODEL_POLICY' ? evaluationJudgePolicy.spec.routes.map((route) => endpointHost(route.provider.endpoint)) : []),
    ...(tool ? [endpointHost(tool.endpoint)] : []),
  ].filter((value, index, values) => values.indexOf(value) === index)
  return {
    kind: 'AGENT',
    ...shared,
    description: draft.description.trim(),
    instructions: draft.instructions.trim(),
    inputSchema: schemaPresets[draft.inputPreset],
    outputSchema: schemaPresets[draft.outputPreset],
    modelPolicy: { key: modelPolicy.key, revision: modelPolicy.revision },
    prompts: prompt ? [{ key: prompt.key, revision: prompt.revision, order: 10 }] : [],
    skills: skill ? [{ key: skill.key, revision: skill.revision }] : [],
    tools: tool ? [{
      connectionKey: tool.connectionKey,
      connectionRevision: tool.connectionRevision,
      toolName: tool.toolName,
      schemaDigest: tool.schemaDigest,
    }] : [],
    memoryPolicy: {
      scope: draft.memoryScope,
      maxBytes: draft.memoryScope === 'NONE' ? 0 : 1_000_000,
      retentionSeconds: draft.memoryScope === 'NONE' ? 0 : 86_400,
      redact: true,
      sharedScope: draft.memoryScope === 'SHARED' ? draft.sharedScope.trim() : null,
    },
    permissions: {
      delegatedCapabilities,
      toolAllowlist: tool ? [tool.toolName] : [],
      secretScopes,
      networkHosts,
      filesystemReadRoots: [],
      filesystemWriteRoots: [],
      allowHighImpactTools: false,
    },
    hardLimits: {
      maxTotalTokens: draft.maxTotalTokens,
      maxCostUsd: draft.maxCostUsd,
      maxDurationSeconds: draft.maxDurationSeconds,
      maxToolCalls: tool ? draft.maxToolCalls : 0,
      maxTurns: draft.maxTurns,
      maxLoopIterations: 0,
      maxRecursionDepth: 0,
      maxConcurrency: 1,
    },
    evaluationPolicy: {
      requiredEvaluations: ['schema', ...(evaluation ? [evaluation.key] : [])],
      evaluations: evaluation ? [{ key: evaluation.key, revision: evaluation.revision }] : [],
      requireHumanRelease: draft.requireHumanRelease || tool?.impact === 'HIGH_IMPACT',
    },
  }
}
