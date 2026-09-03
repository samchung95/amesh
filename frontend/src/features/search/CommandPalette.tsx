import { Command } from 'cmdk'
import { Clock3, CornerDownLeft, FileCode2, Route, Search, Workflow } from 'lucide-react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'

import type { UiSession } from '../../api/types'
import { compactId } from '../../app/format'
import { navigationItems } from '../../app/navigation'
import { useExecutions, useFlows, useGlobalSearch } from '../../app/queries'
import { useAppSettings } from '../../app/settings'
import { searchResultPath, searchTypeLabel } from './searchModel'

interface CommandPaletteProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  session: UiSession
}

export function CommandPalette({ open, onOpenChange, session }: CommandPaletteProps) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { settings } = useAppSettings()
  const [query, setQuery] = useState('')
  const flows = useFlows(open && session.capabilities['flows.view'])
  const executions = useExecutions(open && session.capabilities['executions.view'])
  const search = useGlobalSearch(query, open && session.capabilities['search.view'])

  const select = (path: string) => {
    void navigate(path)
    onOpenChange(false)
  }

  return (
    <Command.Dialog
      className="command-root"
      contentClassName="command-dialog"
      overlayClassName="command-overlay"
      open={open}
      onOpenChange={onOpenChange}
      label="Global command menu"
    >
      <div className="command-input-row">
        <Search size={20} aria-hidden="true" />
        <Command.Input autoFocus placeholder={t('search')} aria-label={t('search')} value={query} onValueChange={setQuery} />
        <kbd>ESC</kbd>
      </div>
      <Command.List>
        <Command.Empty>
          <Search size={24} aria-hidden="true" />
          {t('noResults')}
        </Command.Empty>
        <Command.Group heading={t('navigation')}>
          {navigationItems.map((item) => {
            const allowed = !item.capability || session.capabilities[item.capability]
            if (!allowed) return null
            const Icon = item.icon
            return (
              <Command.Item key={item.id} value={`${t(item.labelKey)} ${item.path}`} onSelect={() => select(item.path)}>
                <Icon size={17} aria-hidden="true" />
                <span>{t(item.labelKey)}</span>
                <small>{item.path}</small>
                <CornerDownLeft size={14} aria-hidden="true" />
              </Command.Item>
            )
          })}
        </Command.Group>
        {settings.savedViews.length ? (
          <Command.Group heading="Saved views">
            {settings.savedViews.map((view) => (
              <Command.Item key={view.id} value={`${view.label} ${view.path}`} onSelect={() => select(view.path)}>
                <Route size={17} aria-hidden="true" />
                <span>{view.label}</span>
                <small>{view.path}</small>
              </Command.Item>
            ))}
          </Command.Group>
        ) : null}
        {search.data?.items.length ? (
          <Command.Group heading="Indexed resources">
            {search.data.items.map((item) => (
              <Command.Item
                key={`${item.documentType}:${item.documentId}`}
                value={`${item.title} ${item.summary} ${item.namespace || ''} ${item.state || ''}`}
                onSelect={() => select(searchResultPath(item))}
              >
                <Search size={17} aria-hidden="true" />
                <span>{item.title}</span>
                <small>{searchTypeLabel(item.documentType)}{item.namespace ? ` · ${item.namespace}` : ''}</small>
              </Command.Item>
            ))}
            <Command.Item value={`all indexed results ${query}`} onSelect={() => select(`/search?q=${encodeURIComponent(query)}`)}>
              <CornerDownLeft size={17} aria-hidden="true" />
              <span>View all indexed results</span>
              <small>/search</small>
            </Command.Item>
          </Command.Group>
        ) : null}
        {flows.data?.length ? (
          <Command.Group heading={t('flows')}>
            {flows.data.slice(0, 20).map((flow) => (
              <Command.Item
                key={flow.resource_id}
                value={`${flow.namespace} ${flow.flow_id}`}
                onSelect={() => select(`/flows?namespace=${encodeURIComponent(flow.namespace)}&flow=${encodeURIComponent(flow.flow_id)}`)}
              >
                <Workflow size={17} aria-hidden="true" />
                <span>{flow.flow_id}</span>
                <small>{flow.namespace}</small>
              </Command.Item>
            ))}
          </Command.Group>
        ) : null}
        {executions.data?.length ? (
          <Command.Group heading={t('executions')}>
            {executions.data.slice(0, 20).map((execution) => (
              <Command.Item
                key={execution.execution_id}
                value={`${execution.flow_id} ${execution.execution_id} ${execution.state}`}
                onSelect={() => select(`/executions/${execution.execution_id}`)}
              >
                <Clock3 size={17} aria-hidden="true" />
                <span>{execution.flow_id}</span>
                <small>{compactId(execution.execution_id)}</small>
              </Command.Item>
            ))}
          </Command.Group>
        ) : null}
      </Command.List>
      <div className="command-footer">
        <span><FileCode2 size={14} aria-hidden="true" /> Search indexed resources and navigation</span>
        <span><kbd>↑</kbd><kbd>↓</kbd> move <kbd>↵</kbd> open</span>
      </div>
    </Command.Dialog>
  )
}
