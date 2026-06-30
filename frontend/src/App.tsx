import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Actions from './pages/Actions'
import Sheets from './pages/Sheets'

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/actions" element={<Actions />} />
          <Route path="/sheets" element={<Sheets />} />
        </Routes>
      </Layout>
    </Box>
  )
}

export default App
