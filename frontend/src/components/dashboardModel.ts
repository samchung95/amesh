import type {
  DashboardAggregation,
  DashboardDataSource,
  DashboardFilters,
  DashboardMeasure,
  DashboardSpec,
  DashboardVisualization,
} from '../api/types'

export const DASHBOARD_SOURCES: DashboardDataSource[] = ['EXECUTIONS', 'LOGS', 'METRICS', 'SLA', 'WORKERS', 'ASSETS']
export const DASHBOARD_VISUALIZATIONS: DashboardVisualization[] = ['TIME_SERIES', 'TABLE', 'COUNTER', 'DISTRIBUTION', 'STATUS_BREAKDOWN', 'RANKED_LIST']
export const DASHBOARD_AGGREGATIONS: DashboardAggregation[] = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'P50', 'P95']
const FIXED_DIMENSIONS = new Set(['namespace', 'flow', 'state', 'workerGroup', 'level', 'metricName', 'assetType', 'provider', 'outcome', 'checkType', 'unit'])

export interface DashboardFilterDraft {
  hours: number
  namespace: string
  flowId: string
  states: string
  workerGroups: string
  labels: string
  dimensions: string
}

export interface DashboardEditorDraft {
  dashboardId: string
  title: string
  description: string
  visibility: 'PRIVATE' | 'TENANT'
  viewerIds: string
  editorIds: string
  widgetTitle: string
  source: DashboardDataSource
  visualization: DashboardVisualization
  measure: DashboardMeasure
  aggregation: DashboardAggregation
  groupBy: string
  limit: number
  timeoutMs: number
  sampleRate: number
}

export function parsePairs(value: string): Record<string, string> {
  if (!value.trim()) return {}
  return Object.fromEntries(value.split(',').map((pair) => {
    const separator = pair.indexOf('=')
    if (separator < 1 || separator === pair.length - 1) throw new Error(`Expected key=value, received "${pair.trim()}"`)
    return [pair.slice(0, separator).trim(), pair.slice(separator + 1).trim()]
  }))
}

export function dashboardFilters(draft: DashboardFilterDraft, now = new Date()): DashboardFilters {
  const to = now.toISOString()
  const from = new Date(now.getTime() - draft.hours * 3_600_000).toISOString()
  return {
    from,
    to,
    namespace: draft.namespace.trim() || null,
    flowId: draft.flowId.trim() || null,
    states: draft.states.split(',').map((item) => item.trim()).filter(Boolean),
    workerGroups: draft.workerGroups.split(',').map((item) => item.trim()).filter(Boolean),
    labels: parsePairs(draft.labels),
    dimensions: parsePairs(draft.dimensions),
  }
}

export function buildDashboardSpec(draft: DashboardEditorDraft, filters: DashboardFilters): DashboardSpec {
  if (!/^[a-z][a-z0-9_.-]{0,127}$/.test(draft.dashboardId)) throw new Error('Dashboard ID must start with a lowercase letter and use lowercase letters, numbers, dots, dashes or underscores.')
  if (!draft.title.trim() || !draft.widgetTitle.trim()) throw new Error('Dashboard and widget titles are required.')
  const groupBy = draft.groupBy.split(',').map((item) => item.trim()).filter(Boolean)
  if (groupBy.length > 3) throw new Error('At most three group dimensions are allowed.')
  const invalid = groupBy.filter((item) => !FIXED_DIMENSIONS.has(item) && !/^(label|dimension)\.[A-Za-z0-9_.-]{1,64}$/.test(item))
  if (invalid.length) throw new Error(`Unsupported dimensions: ${invalid.join(', ')}`)
  const allowedMeasures: Record<DashboardDataSource, DashboardMeasure[]> = {
    EXECUTIONS: ['COUNT', 'DURATION_MS'],
    LOGS: ['COUNT'],
    METRICS: ['COUNT', 'VALUE'],
    SLA: ['COUNT'],
    WORKERS: ['COUNT'],
    ASSETS: ['COUNT'],
  }
  if (!allowedMeasures[draft.source].includes(draft.measure)) throw new Error(`${draft.measure} is not available for ${draft.source}.`)
  if (draft.measure === 'COUNT' && draft.aggregation !== 'COUNT') throw new Error('COUNT measures require COUNT aggregation.')
  return {
    title: draft.title.trim(),
    description: draft.description.trim(),
    visibility: draft.visibility,
    viewerIds: draft.viewerIds.split(',').map((item) => item.trim()).filter(Boolean),
    editorIds: draft.editorIds.split(',').map((item) => item.trim()).filter(Boolean),
    source: 'API',
    widgets: [{
      widgetId: 'primary',
      title: draft.widgetTitle.trim(),
      description: '',
      query: {
        source: draft.source,
        visualization: draft.visualization,
        measure: draft.measure,
        aggregation: draft.aggregation,
        groupBy,
        filters,
        limit: Math.min(500, Math.max(1, draft.limit)),
        timeoutMs: Math.min(5000, Math.max(100, draft.timeoutMs)),
        sampleRate: Math.min(1, Math.max(0.01, draft.sampleRate)),
      },
    }],
  }
}

export function normalizedChartValues(rows: Array<Record<string, unknown>>): number[] {
  const values = rows.map((row) => Number(row.value) || 0)
  const maximum = Math.max(...values, 1)
  return values.map((value) => Math.max(0, Math.min(1, value / maximum)))
}

export function rowLabel(row: Record<string, unknown>): string {
  const parts = Object.entries(row)
    .filter(([key]) => key !== 'value' && key !== 'occurredAt')
    .map(([, value]) => displayValue(value))
  return parts.join(' / ') || 'Total'
}

export function displayValue(value: unknown): string {
  if (value === null || value === undefined) return 'Unspecified'
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return String(value)
  return JSON.stringify(value)
}
