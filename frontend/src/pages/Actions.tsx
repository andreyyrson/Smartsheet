import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  TextField,
  CircularProgress,
  Pagination,
} from '@mui/material'

import api from '../api/client'

interface Action {
  id: string
  title: string | null
  status: string | null
  priority: string | null
  owner: string | null
  department: string | null
  due_date: string | null
  progress: number | null
  is_completed: boolean
}

interface ActionListResponse {
  total: number
  items: Action[]
}

function Actions() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const limit = 25

  const { data, isLoading } = useQuery<ActionListResponse>({
    queryKey: ['actions', page, search],
    queryFn: async () => {
      const response = await api.get('/actions', {
        params: { offset: (page - 1) * limit, limit, search },
      })
      return response.data
    },
  })

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
        Action Command Center
      </Typography>
      <TextField
        label="Buscar ações"
        variant="outlined"
        fullWidth
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        sx={{ mb: 2, backgroundColor: '#1E293B' }}
      />
      {isLoading ? (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <TableContainer component={Paper} sx={{ backgroundColor: '#1E293B' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Atividade</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Prioridade</TableCell>
                  <TableCell>Responsável</TableCell>
                  <TableCell>Prazo</TableCell>
                  <TableCell>Progresso</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data?.items.map((action) => (
                  <TableRow key={action.id}>
                    <TableCell>{action.title}</TableCell>
                    <TableCell>{action.status}</TableCell>
                    <TableCell>{action.priority}</TableCell>
                    <TableCell>{action.owner}</TableCell>
                    <TableCell>{action.due_date}</TableCell>
                    <TableCell>{action.is_completed ? '100%' : `${action.progress ?? 0}%`}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Box display="flex" justifyContent="center" mt={2}>
            <Pagination
              count={Math.ceil((data?.total ?? 0) / limit)}
              page={page}
              onChange={(_, value) => setPage(value)}
              color="primary"
            />
          </Box>
        </>
      )}
    </Box>
  )
}

export default Actions
