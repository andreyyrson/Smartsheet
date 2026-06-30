import {
  Box,
  Button,
  MenuItem,
  Paper,
  TextField,
} from '@mui/material'
import RestartAltIcon from '@mui/icons-material/RestartAlt'

import type { DashboardFilters, FilterOptions } from '../types/dashboard'
import { EMPTY_FILTERS } from '../types/dashboard'

interface Props {
  filters: DashboardFilters
  options?: FilterOptions
  onChange: (filters: DashboardFilters) => void
}

function FilterBar({ filters, options, onChange }: Props) {
  const update = (key: keyof DashboardFilters, value: string) =>
    onChange({ ...filters, [key]: value })

  const selectSx = { minWidth: 180, backgroundColor: '#0F172A' }

  return (
    <Paper
      sx={{
        p: 2,
        mb: 3,
        backgroundColor: '#1E293B',
        display: 'flex',
        flexWrap: 'wrap',
        gap: 2,
        alignItems: 'center',
      }}
    >
      <TextField
        select
        label="Projeto"
        size="small"
        value={filters.projeto}
        onChange={(e) => update('projeto', e.target.value)}
        sx={{ ...selectSx, minWidth: 240 }}
      >
        <MenuItem value="">Todos</MenuItem>
        {options?.projetos.map((p) => (
          <MenuItem key={p} value={p}>
            {p}
          </MenuItem>
        ))}
      </TextField>

      <TextField
        select
        label="Consultor"
        size="small"
        value={filters.consultor}
        onChange={(e) => update('consultor', e.target.value)}
        sx={selectSx}
      >
        <MenuItem value="">Todos</MenuItem>
        {options?.consultores.map((c) => (
          <MenuItem key={c} value={c}>
            {c}
          </MenuItem>
        ))}
      </TextField>

      <TextField
        select
        label="Analista"
        size="small"
        value={filters.analista}
        onChange={(e) => update('analista', e.target.value)}
        sx={selectSx}
      >
        <MenuItem value="">Todos</MenuItem>
        {options?.analistas.map((a) => (
          <MenuItem key={a} value={a}>
            {a}
          </MenuItem>
        ))}
      </TextField>

      <TextField
        select
        label="Status"
        size="small"
        value={filters.status}
        onChange={(e) => update('status', e.target.value)}
        sx={selectSx}
      >
        <MenuItem value="">Todos</MenuItem>
        {options?.status.map((s) => (
          <MenuItem key={s} value={s}>
            {s}
          </MenuItem>
        ))}
      </TextField>

      <TextField
        type="date"
        label="De"
        size="small"
        InputLabelProps={{ shrink: true }}
        value={filters.date_from}
        onChange={(e) => update('date_from', e.target.value)}
        sx={{ backgroundColor: '#0F172A' }}
      />
      <TextField
        type="date"
        label="Até"
        size="small"
        InputLabelProps={{ shrink: true }}
        value={filters.date_to}
        onChange={(e) => update('date_to', e.target.value)}
        sx={{ backgroundColor: '#0F172A' }}
      />

      <Box flexGrow={1} />
      <Button
        variant="outlined"
        startIcon={<RestartAltIcon />}
        onClick={() => onChange({ ...EMPTY_FILTERS })}
      >
        Limpar
      </Button>
    </Paper>
  )
}

export default FilterBar
