import { Box, Card, CardContent, Chip, Typography } from '@mui/material'
import { motion } from 'framer-motion'
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { DashboardCharts } from '../types/dashboard'
import { chartColors } from '../theme/colors'

interface Props {
  data?: DashboardCharts
  onProjectClick?: (project: string) => void
}

const MotionCard = motion(Card)

function shorten(label: string, max = 18) {
  return label.length > max ? `${label.slice(0, max)}…` : label
}

function ChartCard({
  title,
  data,
  color,
  delay,
  horizontal = false,
  onProjectClick,
}: {
  title: string
  data: { label: string; value: number }[]
  color: string
  delay: number
  horizontal?: boolean
  onProjectClick?: (project: string) => void
}) {
  const chartData = data.map((d) => ({ ...d, short: shorten(d.label, horizontal ? 24 : 18) }))
  return (
    <MotionCard
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      sx={{ backgroundColor: '#1E293B', height: '100%' }}
    >
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart
            data={chartData}
            layout={horizontal ? 'vertical' : 'horizontal'}
            margin={horizontal ? { top: 8, right: 40, bottom: 8, left: 8 } : { top: 8, right: 8, bottom: 40, left: -10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={horizontal} />
            {horizontal ? (
              <>
                <XAxis type="number" tick={{ fill: '#94A3B8', fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="short"
                  tick={{ fill: '#94A3B8', fontSize: 11 }}
                  width={120}
                />
              </>
            ) : (
              <>
                <XAxis
                  dataKey="short"
                  tick={{ fill: '#94A3B8', fontSize: 11 }}
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} allowDecimals={false} />
              </>
            )}
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F172A',
                border: '1px solid #334155',
                borderRadius: 8,
                color: '#F8FAFC',
              }}
              cursor={{ fill: 'rgba(148,163,184,0.1)' }}
              labelFormatter={(_, payload) =>
                payload && payload.length ? payload[0].payload.label : ''
              }
            />
            <Bar
              dataKey="value"
              fill={color}
              radius={horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]}
              animationDuration={700}
              onClick={(data) => onProjectClick?.(data.label)}
              cursor={onProjectClick ? 'pointer' : 'default'}
            >
              <LabelList dataKey="value" position={horizontal ? 'right' : 'top'} fill="#F8FAFC" fontSize={11} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </MotionCard>
  )
}

function AlertChartCard({
  title,
  data,
  delay,
  onProjectClick,
}: {
  title: string
  data: { label: string; value: number }[]
  delay: number
  onProjectClick?: (project: string) => void
}) {
  const chartData = data.map((d) => ({ ...d, short: shorten(d.label, 24) }))
  return (
    <MotionCard
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      sx={{
        backgroundColor: '#1E293B',
        height: '100%',
        border: '1px solid rgba(239,68,68,0.4)',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#EF4444' }}>
            {title}
          </Typography>
          <Chip label={data.length} size="small" color="error" />
        </Box>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 8, right: 40, bottom: 8, left: 8 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
            <XAxis type="number" tick={{ fill: '#94A3B8', fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="short"
              tick={{ fill: '#94A3B8', fontSize: 11 }}
              width={120}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F172A',
                border: '1px solid #334155',
                borderRadius: 8,
                color: '#F8FAFC',
              }}
              labelFormatter={(_, payload) =>
                payload && payload.length ? payload[0].payload.label : ''
              }
            />
            <Bar
              dataKey="value"
              fill="#EF4444"
              radius={[0, 4, 4, 0]}
              animationDuration={700}
              onClick={(data) => onProjectClick?.(data.label)}
              cursor={onProjectClick ? 'pointer' : 'default'}
            >
              <LabelList dataKey="value" position="right" fill="#F8FAFC" fontSize={11} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </MotionCard>
  )
}

function BarCharts({ data, onProjectClick }: Props) {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' },
        gap: 3,
        mb: 3,
      }}
    >
      <ChartCard
        title="Ações por Projeto"
        data={(data?.actions_by_project ?? []).slice(0, 12)}
        color={chartColors.primary}
        delay={0.05}
        horizontal
        onProjectClick={onProjectClick}
      />
      <ChartCard
        title="Ações em Andamento por Projeto"
        data={(data?.in_progress_by_project ?? []).slice(0, 12)}
        color={chartColors.secondary}
        delay={0.1}
        horizontal
        onProjectClick={onProjectClick}
      />
      <Box sx={{ gridColumn: { md: '1 / -1' } }}>
        <AlertChartCard
          title="Empresas com menos de 50 ações (atenção)"
          data={data?.small_projects_alert ?? []}
          delay={0.15}
          onProjectClick={onProjectClick}
        />
      </Box>
    </Box>
  )
}

export default BarCharts
