import { type FormEvent, useEffect, useId, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Bell,
  CheckCircle2,
  ChevronDown,
  Command as CommandIcon,
  Languages,
  LockKeyhole,
  Menu,
  Radio,
  Search,
  ServerCog,
  X,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { NavLink, Outlet } from 'react-router-dom'

import type { UiSession } from '../api/types'
import { CommandPalette } from '../features/search'
import { CatalogSelect } from '../shared/ui'
import { groupIcons, navigationItems, type NavigationGroup } from './navigation'
import { useApiClient, useFlows } from './queries'
import { useAppSettings } from './settings'

const groups: NavigationGroup[] = ['build', 'operate', 'govern']

export function AppShell({ session }: { session: UiSession }) {
  const { t, i18n } = useTranslation()
  const { settings, disconnect, updateContext, updateLocale, updateTimezone } = useAppSettings()
  const api = useApiClient()
  const [commandOpen, setCommandOpen] = useState(false)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [contextOpen, setContextOpen] = useState(false)
  const notificationId = useId()
  const announcements = useQuery({
    queryKey: ['announcements', settings.tenant, settings.namespace],
    queryFn: () => api.announcements(settings.namespace || undefined),
    enabled: session.capabilities['announcements.view'],
    refetchInterval: 10_000,
  })
  const flows = useFlows(session.capabilities['flows.view'])
  const contextNamespaces = Array.from(new Set([
    ...(settings.namespace ? [settings.namespace] : []),
    ...(flows.data || []).map((flow) => flow.namespace),
  ])).sort()

  useEffect(() => {
    void i18n.changeLanguage(settings.locale)
    document.documentElement.lang = settings.locale
  }, [i18n, settings.locale])

  useEffect(() => {
    const handleShortcut = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === 'k' && (event.metaKey || event.ctrlKey)) {
        event.preventDefault()
        setCommandOpen((value) => !value)
      }
    }
    document.addEventListener('keydown', handleShortcut)
    return () => document.removeEventListener('keydown', handleShortcut)
  }, [])

  const signOut = async () => {
    try {
      if (settings.authenticationMode === 'session') await api.logout()
    } finally {
      disconnect()
    }
  }

  return (
    <div className="app-layout">
      <a className="skip-link" href="#main-content">{t('skip')}</a>
      <aside className={`app-rail ${mobileNavOpen ? 'app-rail-open' : ''}`} aria-label="Primary">
        <div className="rail-brand">
          <div className="brand-mark brand-mark-small" aria-hidden="true"><span /><span /><span /></div>
          <div>
            <strong>{t('brand')}</strong>
            <small>{t('product')}</small>
          </div>
          <button className="icon-button rail-mobile-close" type="button" onClick={() => setMobileNavOpen(false)} aria-label="Close navigation">
            <X size={20} aria-hidden="true" />
          </button>
        </div>
        <nav className="rail-navigation">
          {groups.map((group) => {
            const GroupIcon = groupIcons[group]
            const items = navigationItems.filter((item) => item.group === group)
            return (
              <section key={group} className="rail-group" aria-labelledby={`nav-${group}`}>
                <h2 id={`nav-${group}`}><GroupIcon size={13} aria-hidden="true" />{t(group)}</h2>
                {items.map((item) => {
                  const allowed = !item.capability || session.capabilities[item.capability]
                  const Icon = item.icon
                  if (!allowed) {
                    return (
                      <span key={item.id} className="rail-link rail-link-disabled" role="link" aria-label={t(item.labelKey)} aria-disabled="true" title={t('permissionDenied')}>
                        <Icon size={19} aria-hidden="true" />
                        <span>{t(item.labelKey)}</span>
                        <LockKeyhole className="rail-lock" size={13} aria-hidden="true" />
                      </span>
                    )
                  }
                  return (
                    <NavLink key={item.id} to={item.path} end={item.path === '/'} aria-label={t(item.labelKey)} onClick={() => setMobileNavOpen(false)} className={({ isActive }) => `rail-link ${isActive ? 'rail-link-active' : ''}`}>
                      <Icon size={19} aria-hidden="true" />
                      <span>{t(item.labelKey)}</span>
                    </NavLink>
                  )
                })}
              </section>
            )
          })}
        </nav>
        <div className="rail-foot">
          <span className="connection-pulse"><i />API connected</span>
          <small>server / {session.serverVersion}</small>
        </div>
      </aside>
      {mobileNavOpen ? <button className="mobile-scrim" type="button" onClick={() => setMobileNavOpen(false)} aria-label="Close navigation overlay" /> : null}
      <div className="app-workspace">
        <header className="top-bar">
          <button className="icon-button mobile-menu" type="button" onClick={() => setMobileNavOpen(true)} aria-label="Open navigation">
            <Menu size={21} aria-hidden="true" />
          </button>
          <button className="context-trigger" type="button" onClick={() => setContextOpen((value) => !value)} aria-expanded={contextOpen} aria-controls="workspace-context-popover">
            <span><small>Tenant</small><strong>{settings.tenant}</strong></span>
            <span className="context-divider" aria-hidden="true" />
            <span><small>Namespace</small><strong>{settings.namespace || 'All namespaces'}</strong></span>
            <ChevronDown size={16} aria-hidden="true" />
          </button>
          {contextOpen ? (
            <ContextPopover tenant={settings.tenant} namespace={settings.namespace} namespaces={contextNamespaces} loading={flows.isPending} onApply={(tenant, namespace) => { updateContext(tenant, namespace); setContextOpen(false) }} />
          ) : null}
          <button className="command-trigger" type="button" onClick={() => setCommandOpen(true)} aria-label={t('search')}>
            <Search size={18} aria-hidden="true" />
            <span>{t('search')}</span>
            <kbd><CommandIcon size={12} aria-hidden="true" />K</kbd>
          </button>
          <div className="top-actions">
            <label className="select-icon" title="Language">
              <Languages size={18} aria-hidden="true" />
              <span className="sr-only">Language</span>
              <select value={settings.locale} onChange={(event) => updateLocale(event.target.value === 'zh-CN' ? 'zh-CN' : 'en')} aria-label="Language">
                <option value="en">EN</option>
                <option value="zh-CN">中文</option>
              </select>
            </label>
            <label className="timezone-control">
              <span className="sr-only">Time zone</span>
              <select value={settings.timezone} onChange={(event) => updateTimezone(event.target.value)} aria-label="Time zone">
                <option value="UTC">UTC</option>
                <option value="Asia/Singapore">SGT</option>
                <option value="America/New_York">New York</option>
                <option value="Europe/London">London</option>
              </select>
            </label>
            <button className="icon-button notification-button" type="button" onClick={() => setNotificationsOpen((value) => !value)} aria-expanded={notificationsOpen} aria-controls={notificationId} aria-label={t('notifications')}>
              <Bell size={19} aria-hidden="true" /><i aria-hidden="true" />
            </button>
            <button className="avatar-button" type="button" onClick={() => void signOut()} title={t('disconnect')} aria-label={`${session.display}. ${t('disconnect')}`}>
              {session.display.slice(0, 2).toUpperCase()}
            </button>
          </div>
          {notificationsOpen ? <NotificationPopover id={notificationId} telemetryEnabled={session.telemetryEnabled} /> : null}
        </header>
        {announcements.data?.length ? (
          <section className="announcement-stack" aria-label="Operational announcements" aria-live="polite">
            {announcements.data.map((announcement) => (
              <article className={`announcement-banner announcement-${announcement.severity.toLowerCase()}`} key={announcement.id}>
                <strong>{announcement.title}</strong>
                <span>{announcement.message}</span>
                <small>Until {new Date(announcement.expiresAt).toLocaleString()}</small>
              </article>
            ))}
          </section>
        ) : null}
        <main id="main-content" className="main-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
      <CommandPalette open={commandOpen} onOpenChange={setCommandOpen} session={session} />
    </div>
  )
}

function ContextPopover({ tenant, namespace, namespaces, loading, onApply }: { tenant: string; namespace: string; namespaces: string[]; loading: boolean; onApply: (tenant: string, namespace: string) => void }) {
  const [nextTenant, setNextTenant] = useState(tenant)
  const [nextNamespace, setNextNamespace] = useState(namespace)
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    onApply(nextTenant, nextNamespace)
  }
  return (
    <form id="workspace-context-popover" className="popover context-popover" onSubmit={submit}>
      <p className="popover-title"><ServerCog size={17} aria-hidden="true" />Workspace context</p>
      <CatalogSelect label="Tenant" value={nextTenant} options={[{ value: tenant, label: `${tenant} · current tenant` }]} onChange={setNextTenant} emptyLabel="Select tenant" required />
      <CatalogSelect label="Namespace filter" value={nextNamespace} options={namespaces.map((item) => ({ value: item, label: item }))} onChange={setNextNamespace} emptyLabel="All namespaces" loading={loading} />
      <button className="button button-primary" type="submit">Apply context</button>
    </form>
  )
}

function NotificationPopover({ id, telemetryEnabled }: { id: string; telemetryEnabled: boolean }) {
  return (
    <aside id={id} className="popover notification-popover" aria-label="Notifications" aria-live="polite">
      <p className="popover-title"><Bell size={17} aria-hidden="true" />System notices</p>
      <article><CheckCircle2 size={18} aria-hidden="true" /><div><strong>API connection healthy</strong><small>Authenticated workspace session is active.</small></div></article>
      <article><Radio size={18} aria-hidden="true" /><div><strong>Product telemetry {telemetryEnabled ? 'enabled' : 'disabled'}</strong><small>{telemetryEnabled ? 'Enabled by deployment policy.' : 'No analytics leave this browser.'}</small></div></article>
    </aside>
  )
}
