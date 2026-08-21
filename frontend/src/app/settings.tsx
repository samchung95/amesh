import {
  createContext,
  type PropsWithChildren,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'

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
}

export interface AppSettings extends StoredSettings {
  token: string
}

interface SettingsContextValue {
  settings: AppSettings
  connected: boolean
  connect: (token: string, tenant: string) => void
  disconnect: () => void
  updateContext: (tenant: string, namespace: string) => void
  updateLocale: (locale: Locale) => void
  updateTimezone: (timezone: string) => void
  saveView: (view: SavedView) => void
  removeView: (viewId: string) => void
}

const STORAGE_KEY = 'amesh.ui.settings.v1'
const TOKEN_KEY = 'amesh.ui.token'

const defaults: StoredSettings = {
  tenant: 'default',
  namespace: '',
  locale: 'en',
  timezone: 'UTC',
  savedViews: [],
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
    }
  } catch {
    return defaults
  }
}

const SettingsContext = createContext<SettingsContextValue | null>(null)

export function SettingsProvider({ children }: PropsWithChildren) {
  const [stored, setStored] = useState(loadSettings)
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY) || '')

  const persist = useCallback((next: StoredSettings) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    setStored(next)
  }, [])

  const value = useMemo<SettingsContextValue>(
    () => ({
      settings: { ...stored, token },
      connected: token.trim().length > 0,
      connect: (nextToken, tenant) => {
        const normalized = nextToken.trim()
        sessionStorage.setItem(TOKEN_KEY, normalized)
        setToken(normalized)
        persist({ ...stored, tenant: tenant.trim() || 'default' })
      },
      disconnect: () => {
        sessionStorage.removeItem(TOKEN_KEY)
        setToken('')
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
    [persist, stored, token],
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
