import { type FormEvent, useState } from 'react'
import { ArrowRight, KeyRound, Network } from 'lucide-react'
import { useTranslation } from 'react-i18next'

import { useAppSettings } from '../app/settings'

export function ConnectionGate() {
  const { t } = useTranslation()
  const { connect, settings, updateLocale } = useAppSettings()
  const [token, setToken] = useState('')
  const [tenant, setTenant] = useState(settings.tenant)
  const [error, setError] = useState('')

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token.trim()) {
      setError('An API token is required.')
      return
    }
    connect(token, tenant)
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
        <h1 id="connection-title">{t('connect')}</h1>
        <p className="connection-lede">{t('connectDescription')}</p>
        <div className="connection-diagram" aria-hidden="true">
          <span>FLOW</span>
          <i />
          <span>AGENT</span>
          <i />
          <span>RUN</span>
        </div>
      </section>
      <section className="connection-panel" aria-label={t('connect')}>
        <div className="connection-panel-heading">
          <Network size={20} aria-hidden="true" />
          <div>
            <p className="eyebrow">API / v1</p>
            <h2>Workspace connection</h2>
          </div>
        </div>
        <form onSubmit={submit} noValidate>
          <label htmlFor="api-token">{t('apiToken')}</label>
          <div className="input-with-icon">
            <KeyRound size={18} aria-hidden="true" />
            <input
              id="api-token"
              name="token"
              type="password"
              autoComplete="current-password"
              value={token}
              onChange={(event) => {
                setToken(event.target.value)
                setError('')
              }}
              aria-describedby={error ? 'connection-error' : undefined}
              aria-invalid={Boolean(error)}
              autoFocus
            />
          </div>
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
          <button className="button button-primary button-wide" type="submit">
            {t('continue')}
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
          <p>No product telemetry or font CDN requests.</p>
        </div>
      </section>
    </main>
  )
}
