import { Box, Card, CardContent, Typography } from '@mui/material'
import { motion } from 'framer-motion'

import type { DashboardSummary } from '../types/dashboard'
import { kpiColors } from '../theme/colors'

interface Props {
  data?: DashboardSummary
}

const MotionCard = motion(Card)

function KpiCards({ data }: Props) {
  const kpis = [
    { label: 'Projetos', value: data?.total_projects ?? 0, color: kpiColors.projects },
    { label: 'Total de Ações', value: data?.total_actions ?? 0, color: kpiColors.totalActions },
    { label: 'Concluídas', value: data?.completed ?? 0, color: kpiColors.completed },
    { label: 'Em Andamento', value: data?.in_progress ?? 0, color: kpiColors.inProgress },
    { label: 'Em Atraso', value: data?.delayed ?? 0, color: kpiColors.delayed },
    { label: 'Críticas', value: data?.critical ?? 0, color: kpiColors.critical },
    { label: 'Vencendo (7d)', value: data?.due_soon ?? 0, color: kpiColors.dueSoon },
    {
      label: 'Taxa de Conclusão',
      value: `${data?.completion_rate ?? 0}%`,
      color: kpiColors.completionRate,
    },
  ]

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: {
          xs: 'repeat(2, 1fr)',
          sm: 'repeat(3, 1fr)',
          md: 'repeat(4, 1fr)',
        },
        gap: 2,
        mb: 3,
      }}
    >
      {kpis.map((kpi, i) => (
        <MotionCard
          key={kpi.label}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: i * 0.04 }}
          sx={{
            backgroundColor: '#1E293B',
            borderLeft: `4px solid ${kpi.color}`,
          }}
        >
          <CardContent>
            <Typography color="text.secondary" variant="body2" gutterBottom>
              {kpi.label}
            </Typography>
            <motion.div
              key={String(kpi.value)}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Typography variant="h4" sx={{ fontWeight: 700, color: kpi.color }}>
                {kpi.value}
              </Typography>
            </motion.div>
          </CardContent>
        </MotionCard>
      ))}
    </Box>
  )
}

export default KpiCards
