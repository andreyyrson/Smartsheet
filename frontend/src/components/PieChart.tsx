import { Card, CardContent, Typography } from '@mui/material'
import { motion } from 'framer-motion'
import {
  Cell,
  Legend,
  Pie,
  PieChart as RePieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

import type { ChartItem } from '../types/dashboard'
import { colorForStatus } from '../theme/colors'

interface Props {
  title: string
  data?: ChartItem[]
  delay?: number
}

const MotionCard = motion(Card)

function PieChart({ title, data, delay = 0 }: Props) {
  const chartData = data ?? []

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
        <ResponsiveContainer width="100%" height={320}>
          <RePieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="label"
              cx="50%"
              cy="45%"
              outerRadius={110}
              innerRadius={60}
              paddingAngle={2}
              animationDuration={700}
            >
              {chartData.map((d, i) => (
                <Cell key={i} fill={colorForStatus(d.label)} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F172A',
                border: '1px solid #334155',
                borderRadius: 8,
                color: '#F8FAFC',
              }}
              formatter={(value: number, name: string) => [
                <span style={{ color: colorForStatus(name), fontWeight: 600 }}>{value}</span>,
                <span style={{ color: colorForStatus(name) }}>{name}</span>,
              ]}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              wrapperStyle={{ fontSize: 12, color: '#94A3B8' }}
            />
          </RePieChart>
        </ResponsiveContainer>
      </CardContent>
    </MotionCard>
  )
}

export default PieChart
