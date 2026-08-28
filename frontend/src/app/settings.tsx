import {
  createContext,
  type PropsWithChildren,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'
import { useQueryClient, type QueryClient } from '@tanstack/react-query'

export type Locale = 'en' | 'zh-CN'

export interface SavedView {
  id: string
  label: string
  path: string
}

interface StoredSettings {
  tenant: string
  namespace: string
  locale: Locale
  timezone: string
  savedViews: SavedView[]
  authenticationMode: 'session' | 'token'
}

export interface AppSettings extends StoredSettings {
  token: string
}

interface SettingsContextValue {
  settings: AppSettings
  connected: boolean
  connectSession: (tenant: string) => void
  connectToken: (token: string, tenant: string) => void
  disconnect: () => void
  updateContext: (tenant: string, namespace: string) => void
  updateLocale: (locale: Locale) => void
  updateTimezone: (timezone: string) => void
  saveView: (view: SavedView) => void
  removeView: (viewId: string) => void
}

const STORAGE_KEY = 'amesh.ui.settings.v1'
const TOKEN_KEY = 'amesh.ui.token'
const SESSION_FLAG_KEY = 'amesh.ui.browser-session'

const defaults: StoredSettings = {
  tenant: 'default',
  namespace: '',
  locale: 'en',
  timezone: 'UTC',
  savedViews: [],
  authenticationMode: 'session',
}

function clearProtectedQueryState(queryClient: QueryClient) {
  queryClient.clear()
}

function loadSettings(): StoredSettings {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return defaults
  try {
    const stored = JSON.parse(raw) as Partial<StoredSettings>
    return {
      tenant: stored.tenant || defaults.tenant,
      namespace: stored.namespace || '',
      locale: stored.locale === 'zh-CN' ? 'zh-CN' : 'en',
      timezone: stored.timezone || defaults.timezone,
      savedViews: Array.isArray(stored.savedViews) ? stored.savedViews : [],
      authenticationMode: stored.authenticationMode === 'token' ? 'token' : 'session',
    }
  } catch {
    return defaults
  }
}

const SettingsContext = createContext<SettingsContextValue | null>(null)

export function SettingsProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient()
  const [stored, setStored] = useState(loadSettings)
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY) || '')
  const [sessionActive, setSessionActive] = useState(
    () => localStorage.getItem(SESSION_FLAG_KEY) === '1',
  )

  const persist = useCallback((next: StoredSettings) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    setStored(next)
  }, [])

  const value = useMemo<SettingsContextValue>(
    () => ({
      settings: { ...stored, token },
      connected: token.trim().length > 0 || sessionActive,
      connectSession: (tenant) => {
        clearProtectedQueryState(queryClient)
        sessionStorage.removeItem(TOKEN_KEY)
        localStorage.setItem(SESSION_FLAG_KEY, '1')
        setToken('')
        setSessionActive(true)
        persist({
          ...stored,
          tenant: tenant.trim() || 'default',
          authenticationMode: 'session',
        })
      },
      connectToken: (nextToken, tenant) => {
        clearProtectedQueryState(queryClient)
        const normalized = nextToken.trim()
        sessionStorage.setItem(TOKEN_KEY, normalized)
        localStorage.removeItem(SESSION_FLAG_KEY)
        setToken(normalized)
        setSessionActive(false)
        persist({
          ...stored,
          tenant: tenant.trim() || 'default',
          authenticationMode: 'token',
        })
      },
      disconnect: () => {
        clearProtectedQueryState(queryClient)
        sessionStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(SESSION_FLAG_KEY)
        setToken('')
        setSessionActive(false)
      },
      updateContext: (tenant, namespace) =>
        persist({ ...stored, tenant: tenant.trim() || 'default', namespace: namespace.trim() }),
      updateLocale: (locale) => persist({ ...stored, locale }),
      updateTimezone: (timezone) => persist({ ...stored, timezone }),
      saveView: (view) => {
        const savedViews = [...stored.savedViews.filter((item) => item.id !== view.id), view]
        persist({ ...stored, savedViews })
      },
      removeView: (viewId) =>
        persist({ ...stored, savedViews: stored.savedViews.filter((view) => view.id !== viewId) }),
    }),
    [persist, queryClient, sessionActive, stored, token],
  )

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>
}

// This hook intentionally shares the provider module so its private context cannot be misused.
// eslint-disable-next-line react-refresh/only-export-components
export function useAppSettings(): SettingsContextValue {
  const value = useContext(SettingsContext)
  if (!value) throw new Error('useAppSettings must be used inside SettingsProvider')
  return value
}
