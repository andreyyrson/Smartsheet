export interface DashboardSummary {
  total_projects: number
  total_actions: number
  completed: number
  in_progress: number
  delayed: number
  blocked: number
  critical: number
  completion_rate: number
  due_soon: number
  overdue: number
}

export interface ChartItem {
  label: string
  value: number
}

export interface DashboardCharts {
  actions_by_status: ChartItem[]
  actions_by_project: ChartItem[]
  in_progress_by_project: ChartItem[]
  small_projects_alert: ChartItem[]
}

export interface BreakdownRow {
  project: string
  consultor: string | null
  analista: string | null
  total: number
  completed: number
  in_progress: number
  overdue: number
  completion_rate: number
}

export interface FilterOptions {
  projetos: string[]
  consultores: string[]
  analistas: string[]
  status: string[]
}

export interface DashboardFilters {
  projeto: string
  consultor: string
  analista: string
  status: string
  date_from: string
  date_to: string
}

export const EMPTY_FILTERS: DashboardFilters = {
  projeto: '',
  consultor: '',
  analista: '',
  status: '',
  date_from: '',
  date_to: '',
}

export function filtersToParams(f: DashboardFilters): Record<string, string> {
  const params: Record<string, string> = {}
  if (f.projeto) params.projeto = f.projeto
  if (f.consultor) params.consultor = f.consultor
  if (f.analista) params.analista = f.analista
  if (f.status) params.status = f.status
  if (f.date_from) params.date_from = f.date_from
  if (f.date_to) params.date_to = f.date_to
  return params
}
