import type { AgentProgressEvent, AgentProgressFrame } from '../api/types'

export interface AgentProgressTimelineState {
  events: AgentProgressEvent[]
  cursor: string | null
  isTerminal: boolean
}

export interface AgentProgressImageReference {
  reference: string
  mediaType: string | null
  sizeBytes: number
  checksumSha256: string
  altText?: string | null
  thumbnailUrl?: string | null
}

export function progressImagesFromSessionEvents(
  events: Array<{ payload: Record<string, unknown> }>,
): AgentProgressImageReference[] {
  const images: AgentProgressImageReference[] = []
  const seen = new Set<string>()
  for (const event of events) {
    const candidates = event.payload.inputImages
    if (!Array.isArray(candidates)) continue
    for (const candidate of candidates) {
      if (!candidate || typeof candidate !== 'object') continue
      const value = candidate as Record<string, unknown>
      if (
        value.schemaVersion !== 'amesh.image-display/v1'
        || typeof value.reference !== 'string'
        || typeof value.checksumSha256 !== 'string'
        || !/^[0-9a-f]{64}$/.test(value.checksumSha256)
        || typeof value.sizeBytes !== 'number'
        || !Number.isSafeInteger(value.sizeBytes)
        || value.sizeBytes < 1
        || (value.mediaType !== null && typeof value.mediaType !== 'string')
      ) continue
      const key = `${value.reference}:${value.checksumSha256}`
      if (seen.has(key)) continue
      seen.add(key)
      images.push({
        reference: value.reference,
        mediaType: value.mediaType,
        sizeBytes: value.sizeBytes,
        checksumSha256: value.checksumSha256,
      })
    }
  }
  return images
}

/** Append server-ordered progress while making reconnects idempotent. */
export function appendAgentProgress(
  current: AgentProgressEvent[],
  incoming: AgentProgressEvent[],
): AgentProgressTimelineState {
  const seenCursors = new Set(current.map((event) => event.cursor))
  const seenIds = new Set(current.map((event) => event.eventId))
  const next = [...current]
  for (const event of incoming) {
    if (seenCursors.has(event.cursor) || seenIds.has(event.eventId)) continue
    seenCursors.add(event.cursor)
    seenIds.add(event.eventId)
    next.push(event)
  }
  const last = next.at(-1)
  return {
    events: next,
    cursor: last?.cursor ?? null,
    isTerminal: last?.frame.activity === 'TERMINAL',
  }
}

export function progressLabel(frame: AgentProgressFrame): string {
  if (frame.detail?.kind === 'STATUS' && frame.detail.label) return frame.detail.label
  if (frame.detail?.kind === 'PUBLIC_SUMMARY') return frame.detail.text
  const activity = frame.activity.toLocaleLowerCase()
  const status = frame.status.toLocaleLowerCase()
  return `${activity} ${status}`
}

export function progressTone(frame: AgentProgressFrame): 'live' | 'success' | 'warning' | 'danger' | 'neutral' {
  if (frame.status === 'FAILED') return 'danger'
  if (frame.status === 'CANCELLED' || frame.status === 'TRUNCATED' || frame.status === 'PAUSED') return 'warning'
  if (frame.status === 'COMPLETED' || frame.activity === 'TERMINAL') return 'success'
  if (frame.status === 'STARTED' || frame.status === 'DELTA') return 'live'
  return 'neutral'
}
