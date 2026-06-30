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
  Typography,
} from '@mui/material'
import { AnimatePresence, motion } from 'framer-motion'

import type { BreakdownRow } from '../types/dashboard'

interface Props {
  rows?: BreakdownRow[]
}

const MotionRow = motion(TableRow)

function SummaryTable({ rows }: Props) {
  return (
    <Paper sx={{ backgroundColor: '#1E293B', p: 2 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
        Resumo por Projeto
      </Typography>
      <TableContainer sx={{ maxHeight: 460 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ backgroundColor: '#0F172A' }}>Projeto</TableCell>
              <TableCell sx={{ backgroundColor: '#0F172A' }}>Consultor</TableCell>
              <TableCell sx={{ backgroundColor: '#0F172A' }}>Analista</TableCell>
              <TableCell align="right" sx={{ backgroundColor: '#0F172A' }}>
                Total
              </TableCell>
              <TableCell align="right" sx={{ backgroundColor: '#0F172A' }}>
                Em Andamento
              </TableCell>
              <TableCell align="right" sx={{ backgroundColor: '#0F172A' }}>
                Atrasadas
              </TableCell>
              <TableCell sx={{ backgroundColor: '#0F172A', minWidth: 160 }}>
                Conclusão
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <AnimatePresence>
              {(rows ?? []).map((row, i) => (
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
