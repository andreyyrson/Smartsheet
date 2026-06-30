import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Box, LinearProgress, Typography } from '@mui/material'

import api from '../api/client'
import BarCharts from '../components/BarCharts'
import FilterBar from '../components/FilterBar'
import KpiCards from '../components/KpiCards'
import PieChart from '../components/PieChart'
import SummaryTable from '../components/SummaryTable'
import type {
  BreakdownRow,
  DashboardCharts,
  DashboardSummary,
  FilterOptions,
} from '../types/dashboard'
import { EMPTY_FILTERS, filtersToParams } from '../types/dashboard'

function Dashboard() {
  const [filters, setFilters] = useState({ ...EMPTY_FILTERS })
  const params = filtersToParams(filters)

  const { data: options } = useQuery<FilterOptions>({
    queryKey: ['filter-options'],
    queryFn: async () => (await api.get('/filters/options')).data,
  })

  const { data: summary, isFetching: loadingSummary } = useQuery<DashboardSummary>({
    queryKey: ['dashboard-summary', params],
    queryFn: async () => (await api.get('/dashboard/summary', { params })).data,
  })

  const { data: charts } = useQuery<DashboardCharts>({
    queryKey: ['dashboard-charts', params],
    queryFn: async () => (await api.get('/dashboard/charts', { params })).data,
  })

  const { data: breakdown } = useQuery<BreakdownRow[]>({
    queryKey: ['dashboard-breakdown', params],
    queryFn: async () => (await api.get('/dashboard/breakdown', { params })).data,
  })

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
        Visão Geral dos Projetos
      </Typography>
      <Box sx={{ height: 4, mb: 1 }}>
        {loadingSummary && <LinearProgress />}
      </Box>

      <FilterBar filters={filters} options={options} onChange={setFilters} />
      <KpiCards data={summary} />
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' },
          gap: 3,
          mb: 3,
        }}
      >
        <PieChart title="Ações por Status" data={charts?.actions_by_status} delay={0.05} />
        <BarCharts data={charts} />
      </Box>
      <SummaryTable rows={breakdown} />
    </Box>
  )
}

export default Dashboard
