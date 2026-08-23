import type { SearchDocument, SearchDocumentType } from '../api/types'

export const SEARCH_TYPES: SearchDocumentType[] = ['FLOW', 'EXECUTION', 'LOG', 'ASSET', 'AUDIT']

export function parseSearchPairs(value: string): Record<string, string> {
  const result: Record<string, string> = {}
  for (const item of value.split(',')) {
    const separator = item.indexOf('=')
    if (separator <= 0) continue
    const key = item.slice(0, separator).trim()
    const itemValue = item.slice(separator + 1).trim()
    if (key && itemValue) result[key] = itemValue
  }
  return result
}

export function searchResultPath(document: SearchDocument): string {
  const flowId = typeof document.fields.flowId === 'string' ? document.fields.flowId : ''
  const executionId = typeof document.fields.executionId === 'string' ? document.fields.executionId : ''
  if (document.documentType === 'FLOW' && document.namespace && flowId) {
    return `/flows/${encodeURIComponent(document.namespace)}/${encodeURIComponent(flowId)}`
  }
  if ((document.documentType === 'EXECUTION' || document.documentType === 'LOG') && executionId) {
    const suffix = document.documentType === 'LOG' ? '?view=logs' : ''
    return `/executions/${encodeURIComponent(executionId)}${suffix}`
  }
  if (document.documentType === 'ASSET') return `/assets?asset=${encodeURIComponent(document.documentId)}`
  if (document.documentType === 'AUDIT') return `/administration?view=audit&event=${encodeURIComponent(document.documentId)}`
  return '/search'
}

export function searchTypeLabel(type: SearchDocumentType): string {
  return ({ FLOW: 'Flow', EXECUTION: 'Execution', LOG: 'Log', ASSET: 'Asset', AUDIT: 'Audit' })[type]
}
