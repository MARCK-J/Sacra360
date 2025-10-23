import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Registros from './pages/Registros'
import Personas from './pages/Personas'
import Auditoria from './pages/Auditoria'
import Digitalizacion from './pages/Digitalizacion'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/registros" element={<Registros />} />
      <Route path="/personas" element={<Personas />} />
      <Route path="/auditoria" element={<Auditoria />} />
      <Route path="/digitalizacion" element={<Digitalizacion />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
