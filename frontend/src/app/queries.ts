import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'

import { createApiClient } from '../api/client'
import { useAppSettings } from './settings'

export function useApiClient() {
  const { settings } = useAppSettings()
  return useMemo(() => createApiClient({
    token: settings.token,
    tenant: settings.tenant,
    namespace: settings.namespace,
  }), [settings.namespace, settings.tenant, settings.token])
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

export function useGlobalSearch(query: string, enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['search', settings.tenant, settings.namespace, query],
    queryFn: () => api.search({
      query,
      namespace: settings.namespace || undefined,
      limit: 20,
    }),
    enabled: enabled && query.trim().length >= 2,
    staleTime: 5_000,
  })
}

export function useTriggerRuntime(enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['triggers', settings.tenant, settings.namespace],
    queryFn: () => api.triggers(settings.namespace || undefined),
    enabled,
    refetchInterval: 10_000,
  })
}

export function useTriggerOccurrences(enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['trigger-occurrences', settings.tenant, settings.namespace],
    queryFn: () => api.triggerOccurrences(settings.namespace || undefined),
    enabled,
    refetchInterval: 10_000,
  })
}

export function useCheckPolicies(enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['check-policies', settings.tenant, settings.namespace],
    queryFn: () => api.checkPolicies(settings.namespace || undefined),
    enabled,
    refetchInterval: 30_000,
  })
}

export function useCheckEvaluations(enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['check-evaluations', settings.tenant, settings.namespace],
    queryFn: () => api.checkEvaluations(settings.namespace || undefined),
    enabled,
    refetchInterval: 10_000,
  })
}

export function useCheckCompliance(enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['check-compliance', settings.tenant, settings.namespace],
    queryFn: () => api.checkCompliance(settings.namespace || undefined),
    enabled,
    refetchInterval: 10_000,
  })
}

export function usePluginRegistry(enabled = true) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  return useQuery({
    queryKey: ['plugin-registry', settings.tenant],
    queryFn: api.pluginRegistry,
    enabled,
    staleTime: 15_000,
  })
}
