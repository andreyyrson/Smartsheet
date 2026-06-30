import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Switch,
} from '@mui/material'

import api from '../api/client'

interface Sheet {
  id: string
  smartsheet_id: number
  name: string
  permalink: string | null
  sync_enabled: boolean
  last_sync_at: string | null
}

function Sheets() {
  const queryClient = useQueryClient()

  const { data: sheets, isLoading } = useQuery<Sheet[]>({
    queryKey: ['sheets'],
    queryFn: async () => {
      const response = await api.get('/sheets')
      return response.data
    },
  })

  const discoverMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/sheets/discover')
      return response.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sheets'] }),
  })

  const syncMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post(`/sheets/${id}/sync`, { full: true })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sheets'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      queryClient.invalidateQueries({ queryKey: ['actions'] })
    },
  })

  const toggleMutation = useMutation({
    mutationFn: async ({ id, enabled }: { id: string; enabled: boolean }) => {
      const endpoint = enabled ? `/sheets/${id}/enable` : `/sheets/${id}/disable`
      const response = await api.patch(endpoint)
      return response.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sheets'] }),
  })

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
        Planilhas Smartsheet
      </Typography>
      <Button
        variant="contained"
        onClick={() => discoverMutation.mutate()}
        disabled={discoverMutation.isPending}
        sx={{ mb: 2 }}
      >
        Descobrir Planilhas
      </Button>
      {isLoading ? (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      ) : (
        sheets?.map((sheet) => (
          <Card key={sheet.id} sx={{ backgroundColor: '#1E293B', mb: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h6">{sheet.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Último sync: {sheet.last_sync_at ?? 'Nunca'}
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={2}>
                  <Switch
                    checked={sheet.sync_enabled}
                    onChange={(e) =>
                      toggleMutation.mutate({ id: sheet.id, enabled: e.target.checked })
                    }
                  />
                  <Button
                    variant="outlined"
                    onClick={() => syncMutation.mutate(sheet.id)}
                    disabled={syncMutation.isPending}
                  >
                    Sincronizar
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  )
}

export default Sheets
