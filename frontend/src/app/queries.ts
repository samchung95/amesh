import { useQuery } from '@tanstack/react-query'

import { createApiClient } from '../api/client'
import { useAppSettings } from './settings'

export function useApiClient() {
  const { settings } = useAppSettings()
  return createApiClient({
    token: settings.token,
    tenant: settings.tenant,
    namespace: settings.namespace,
  })
}

export function useSession() {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['session', settings.tenant, settings.namespace, settings.token],
    queryFn: api.session,
    staleTime: 30_000,
  })
}

export function useFlows(enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['flows', settings.tenant],
    queryFn: api.flows,
    enabled,
    staleTime: 10_000,
  })
}

export function useExecutions(enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['executions', settings.tenant],
    queryFn: api.executions,
    enabled,
    refetchInterval: 15_000,
  })
}
