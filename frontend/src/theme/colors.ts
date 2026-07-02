export const statusColors = {
  completed: '#22C55E', // verde
  inProgress: '#F59E0B', // amarelo/laranja
  delayed: '#EF4444', // vermelho
  critical: '#DC2626', // vermelho escuro
  dueSoon: '#EAB308', // amarelo
  blocked: '#64748B', // cinza
} as const

export const kpiColors = {
  projects: '#3B82F6', // azul
  totalActions: '#6366F1', // índigo
  completed: statusColors.completed,
  inProgress: statusColors.inProgress,
  delayed: statusColors.delayed,
  critical: statusColors.critical,
  dueSoon: statusColors.dueSoon,
  completionRate: statusColors.completed,
} as const

export const chartColors = {
  primary: '#6366F1', // índigo
  secondary: '#F59E0B', // amarelo/laranja
  alert: '#EF4444', // vermelho
  success: '#22C55E', // verde
} as const

export function colorForStatus(label: string): string {
  const lower = label.toLowerCase()
  if (lower.includes('atraso')) return statusColors.delayed
  if (lower.includes('críticas') || lower.includes('criticas')) return statusColors.critical
  if (lower.includes('concluído') || lower.includes('concluido')) return statusColors.completed
  if (lower.includes('em andamento')) return statusColors.inProgress
  if (lower.includes('vencendo')) return statusColors.dueSoon
  if (lower.includes('vence hoje')) return statusColors.dueSoon
  if (lower.includes('aguardando')) return statusColors.inProgress
  if (lower.includes('sem status') || lower.includes('invalid')) return statusColors.blocked
  return statusColors.inProgress
}
