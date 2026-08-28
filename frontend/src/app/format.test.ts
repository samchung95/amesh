import { describe, expect, it } from 'vitest'

import { compactId, formatDate, formatNumber } from './format'

describe('locale-sensitive formatting', () => {
  it('formats numbers using the selected locale', () => {
    expect(formatNumber(12345, 'en')).toBe('12,345')
    expect(formatNumber(12345, 'de')).toBe('12.345')
  })

  it('formats an instant in the selected IANA timezone', () => {
    expect(formatDate('2026-08-21T12:00:00Z', 'en-SG', 'Asia/Singapore')).toContain('8:00')
  })

  it('compacts only long identifiers', () => {
    expect(compactId('short-id')).toBe('short-id')
    expect(compactId('00000000-0000-7000-8000-000000000001')).toBe('00000000…0001')
  })
})
