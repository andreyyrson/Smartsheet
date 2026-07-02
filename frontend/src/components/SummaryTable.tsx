import {
  Box,
  Chip,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Typography,
} from '@mui/material'
import { AnimatePresence, motion } from 'framer-motion'
import { useState } from 'react'

import type { BreakdownRow } from '../types/dashboard'

interface Props {
  rows?: BreakdownRow[]
}

type SortKey = 'project' | 'total' | 'in_progress' | 'overdue' | 'completion_rate'

const MotionRow = motion(TableRow)

function SummaryTable({ rows }: Props) {
  const [orderBy, setOrderBy] = useState<SortKey>('total')
  const [order, setOrder] = useState<'asc' | 'desc'>('desc')

  const handleSort = (key: SortKey) => {
    const isAsc = orderBy === key && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(key)
  }

  const sortedRows = [...(rows ?? [])].sort((a, b) => {
    let aVal: string | number
    let bVal: string | number

    switch (orderBy) {
      case 'project':
        aVal = a.project.toLowerCase()
        bVal = b.project.toLowerCase()
        break
      case 'total':
        aVal = a.total
        bVal = b.total
        break
      case 'in_progress':
        aVal = a.in_progress
        bVal = b.in_progress
        break
      case 'overdue':
        aVal = a.overdue
        bVal = b.overdue
        break
      case 'completion_rate':
        aVal = a.completion_rate
        bVal = b.completion_rate
        break
      default:
        aVal = a.total
        bVal = b.total
    }

    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return order === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
    }
    return order === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number)
  })

  return (
    <Paper sx={{ backgroundColor: '#1E293B', p: 2 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
        Resumo por Projeto
      </Typography>
      <TableContainer sx={{ maxHeight: 460 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ backgroundColor: '#0F172A', cursor: 'pointer' }} onClick={() => handleSort('project')}>
                <TableSortLabel active={orderBy === 'project'} direction={order}>
                  Projeto
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ backgroundColor: '#0F172A' }}>Consultor</TableCell>
              <TableCell sx={{ backgroundColor: '#0F172A' }}>Analista</TableCell>
              <TableCell align="right" sx={{ backgroundColor: '#0F172A', cursor: 'pointer' }} onClick={() => handleSort('total')}>
                <TableSortLabel active={orderBy === 'total'} direction={order}>
                  Total
                </TableSortLabel>
              </TableCell>
              <TableCell align="right" sx={{ backgroundColor: '#0F172A', cursor: 'pointer' }} onClick={() => handleSort('in_progress')}>
                <TableSortLabel active={orderBy === 'in_progress'} direction={order}>
                  Em Andamento
                </TableSortLabel>
              </TableCell>
              <TableCell align="right" sx={{ backgroundColor: '#0F172A', cursor: 'pointer' }} onClick={() => handleSort('overdue')}>
                <TableSortLabel active={orderBy === 'overdue'} direction={order}>
                  Atrasadas
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ backgroundColor: '#0F172A', minWidth: 160, cursor: 'pointer' }} onClick={() => handleSort('completion_rate')}>
                <TableSortLabel active={orderBy === 'completion_rate'} direction={order}>
                  Conclusão
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <AnimatePresence>
              {sortedRows.map((row, i) => (
                <MotionRow
                  key={row.project}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.25, delay: Math.min(i * 0.02, 0.4) }}
                  hover
                >
                  <TableCell>{row.project}</TableCell>
                  <TableCell>
                    {row.consultor ? (
                      <Chip label={row.consultor} size="small" color="primary" />
                    ) : (
                      '—'
                    )}
                  </TableCell>
                  <TableCell>
                    {row.analista ? (
                      <Chip label={row.analista} size="small" color="secondary" />
                    ) : (
                      '—'
                    )}
                  </TableCell>
                  <TableCell align="right">{row.total}</TableCell>
                  <TableCell align="right">{row.in_progress}</TableCell>
                  <TableCell align="right">
                    <Typography
                      component="span"
                      sx={{ color: row.overdue > 0 ? '#EF4444' : 'inherit' }}
                    >
                      {row.overdue}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LinearProgress
                        variant="determinate"
                        value={row.completion_rate}
                        sx={{
                          flexGrow: 1,
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: '#334155',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: '#22C55E',
                          },
                        }}
                      />
                      <Typography variant="caption" sx={{ minWidth: 38 }}>
                        {row.completion_rate}%
                      </Typography>
                    </Box>
                  </TableCell>
                </MotionRow>
              ))}
            </AnimatePresence>
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  )
}

export default SummaryTable
