import {
  Boxes,
  Braces,
  BookOpenCheck,
  Bot,
  Cable,
  ChartNoAxesCombined,
  CircleGauge,
  DatabaseZap,
  LayoutGrid,
  RadioTower,
  Rocket,
  ShieldCheck,
  Settings2,
  Workflow,
  type LucideIcon,
} from 'lucide-react'

import type { Capability } from '../api/types'

export type NavigationGroup = 'build' | 'operate' | 'govern'

export interface NavigationItem {
  id: string
  labelKey: string
  path: string
  group: NavigationGroup
  icon: LucideIcon
  capability?: Capability
}

export const navigationItems: NavigationItem[] = [
  { id: 'dashboard', labelKey: 'dashboard', path: '/', group: 'operate', icon: CircleGauge, capability: 'dashboards.view' },
  {
    id: 'flows',
    labelKey: 'flows',
    path: '/flows',
    group: 'build',
    icon: Workflow,
    capability: 'flows.view',
  },
  {
    id: 'blueprints',
    labelKey: 'blueprints',
    path: '/blueprints',
    group: 'build',
    icon: BookOpenCheck,
    capability: 'flows.view',
  },
  {
    id: 'executions',
    labelKey: 'executions',
    path: '/executions',
    group: 'operate',
    icon: ChartNoAxesCombined,
    capability: 'executions.view',
  },
  {
    id: 'triggers',
    labelKey: 'triggers',
    path: '/triggers',
    group: 'operate',
    icon: RadioTower,
    capability: 'triggers.view',
  },
  {
    id: 'checks',
    labelKey: 'checks',
    path: '/checks',
    group: 'operate',
    icon: ShieldCheck,
    capability: 'checks.view',
  },
  {
    id: 'namespaces',
    labelKey: 'namespaces',
    path: '/namespaces',
    group: 'build',
    icon: Braces,
    capability: 'namespaceResources.read',
  },
  { id: 'assets', labelKey: 'assets', path: '/assets', group: 'build', icon: DatabaseZap, capability: 'assets.view' },
  { id: 'agents', labelKey: 'agents', path: '/agents', group: 'build', icon: Bot, capability: 'agents.view' },
  { id: 'apps', labelKey: 'apps', path: '/apps', group: 'build', icon: LayoutGrid, capability: 'apps.view' },
  {
    id: 'plugins',
    labelKey: 'plugins',
    path: '/plugins',
    group: 'govern',
    icon: Cable,
    capability: 'plugins.view',
  },
  {
    id: 'releases',
    labelKey: 'releases',
    path: '/releases',
    group: 'govern',
    icon: Rocket,
    capability: 'releases.view',
  },
  {
    id: 'administration',
    labelKey: 'administration',
    path: '/administration',
    group: 'govern',
    icon: Settings2,
    capability: 'administration.manage',
  },
]

export const groupIcons: Record<NavigationGroup, LucideIcon> = {
  build: Boxes,
  operate: CircleGauge,
  govern: Settings2,
}
