import {
  Box,
  Button,
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
  TablePagination,
  Typography,
} from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
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
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

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

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const paginatedRows = sortedRows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)

  const handleExportCSV = () => {
    const headers = ['Projeto', 'Consultor', 'Analista', 'Total', 'Em Andamento', 'Atrasadas', 'Conclusão (%)']
    const csvContent = [
      headers.join(','),
      ...sortedRows.map(row =>
        [
          row.project,
          row.consultor || '',
          row.analista || '',
          row.total,
          row.in_progress,
          row.overdue,
          row.completion_rate.toFixed(2),
        ].join(',')
      ),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `dashboard-resumo-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <Paper sx={{ backgroundColor: '#1E293B', p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Resumo por Projeto
        </Typography>
        <Button
          variant="outlined"
          size="small"
          startIcon={<DownloadIcon />}
          onClick={handleExportCSV}
          disabled={!sortedRows.length}
        >
          Exportar CSV
        </Button>
      </Box>
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
              {paginatedRows.map((row, i) => (
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
      <TablePagination
        rowsPerPageOptions={[10, 25, 50, 100]}
        component="div"
        count={sortedRows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="Linhas por página"
        sx={{
          color: '#94A3B8',
          '& .MuiTablePagination-select': { color: '#94A3B8' },
          '& .MuiTablePagination-selectIcon': { color: '#94A3B8' },
          '& .MuiTablePagination-actions': { color: '#94A3B8' },
        }}
      />
    </Paper>
  )
}

export default SummaryTable
