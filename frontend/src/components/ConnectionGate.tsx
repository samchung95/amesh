import { type FormEvent, useState } from 'react'
import { ArrowRight, KeyRound, Network, UserRound } from 'lucide-react'
import { useTranslation } from 'react-i18next'

import { ApiError } from '../api/client'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'

interface ConnectionGateProps {
  onConnected?: () => void
}

export function ConnectionGate({ onConnected }: ConnectionGateProps) {
  const { t } = useTranslation()
  const api = useApiClient()
  const { connectSession, connectToken, settings, updateLocale } = useAppSettings()
  const [mode, setMode] = useState<'session' | 'token'>(settings.authenticationMode)
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState('')
  const [tenant, setTenant] = useState(settings.tenant)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    if (mode === 'token' && !token.trim()) {
      setError(t('tokenRequired'))
      return
    }
    if (mode === 'session' && (!identifier.trim() || !password)) {
      setError(t('credentialsRequired'))
      return
    }
    setBusy(true)
    try {
      if (mode === 'session') {
        await api.login(identifier.trim(), password)
        connectSession(tenant)
      } else {
        connectToken(token, tenant)
      }
      onConnected?.()
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : t('authenticationFailed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="connection-page">
      <section className="connection-brand" aria-labelledby="connection-title">
        <div className="brand-mark" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
        <p className="eyebrow">{t('brand')} / orchestration fabric</p>
        <h1 id="connection-title">{t('signIn')}</h1>
        <p className="connection-lede">{t('signInDescription')}</p>
        <div className="connection-diagram" aria-hidden="true">
          <span>IDENTITY</span>
          <i />
          <span>POLICY</span>
          <i />
          <span>RUN</span>
        </div>
      </section>
      <section className="connection-panel" aria-label={t('signIn')}>
        <div className="connection-panel-heading">
          <Network size={20} aria-hidden="true" />
          <div>
            <p className="eyebrow">AUTH / v1</p>
            <h2>{t('workspaceAccess')}</h2>
          </div>
        </div>
        <div className="authentication-modes" role="group" aria-label={t('authenticationMethod')}>
          <button
            type="button"
            className={mode === 'session' ? 'active' : ''}
            aria-pressed={mode === 'session'}
            onClick={() => {
              setMode('session')
              setError('')
            }}
          >
            {t('localAccount')}
          </button>
          <button
            type="button"
            className={mode === 'token' ? 'active' : ''}
            aria-pressed={mode === 'token'}
            onClick={() => {
              setMode('token')
              setError('')
            }}
          >
            {t('apiToken')}
          </button>
        </div>
        <form onSubmit={(event) => void submit(event)} noValidate>
          {mode === 'session' ? (
            <>
              <label htmlFor="user-handle">{t('userHandle')}</label>
              <div className="input-with-icon">
                <UserRound size={18} aria-hidden="true" />
                <input
                  id="user-handle"
                  name="identifier"
                  autoComplete="username"
                  value={identifier}
                  onChange={(event) => setIdentifier(event.target.value)}
                  autoFocus
                />
              </div>
              <label htmlFor="password">{t('password')}</label>
              <div className="input-with-icon">
                <KeyRound size={18} aria-hidden="true" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  aria-describedby={error ? 'connection-error' : undefined}
                  aria-invalid={Boolean(error)}
                />
              </div>
            </>
          ) : (
            <>
              <label htmlFor="api-token">{t('apiToken')}</label>
              <div className="input-with-icon">
                <KeyRound size={18} aria-hidden="true" />
                <input
                  id="api-token"
                  name="token"
                  type="password"
                  autoComplete="off"
                  value={token}
                  onChange={(event) => setToken(event.target.value)}
                  aria-describedby={error ? 'connection-error' : undefined}
                  aria-invalid={Boolean(error)}
                  autoFocus
                />
              </div>
            </>
          )}
          <label htmlFor="tenant">{t('tenant')}</label>
          <input
            id="tenant"
            name="tenant"
            value={tenant}
            onChange={(event) => setTenant(event.target.value)}
            autoComplete="organization"
          />
          {error ? (
            <p id="connection-error" className="field-error" role="alert">
              {error}
            </p>
          ) : null}
          <button className="button button-primary button-wide" type="submit" disabled={busy}>
            {busy ? t('signingIn') : mode === 'session' ? t('signIn') : t('continue')}
            <ArrowRight size={18} aria-hidden="true" />
          </button>
        </form>
        <div className="connection-footer">
          <label htmlFor="connection-language">Language</label>
          <select
            id="connection-language"
            value={settings.locale}
            onChange={(event) => updateLocale(event.target.value === 'zh-CN' ? 'zh-CN' : 'en')}
          >
            <option value="en">English</option>
            <option value="zh-CN">简体中文</option>
          </select>
          <p>{t('privacyNotice')}</p>
        </div>
      </section>
    </main>
  )
}
