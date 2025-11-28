import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Registros from './pages/Registros'
import Personas from './pages/Personas'
import Auditoria from './pages/Auditoria'
import Digitalizacion from './pages/Digitalizacion'
import RevisionOCR from './pages/RevisionOCR'
import Libros from './pages/Libros'
import Usuarios from './pages/Usuarios'
import Reportes from './pages/Reportes'
import Certificados from './pages/Certificados'
import Sacramento from './pages/Sacramento'
import Sacramentos from './pages/Sacramentos'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/registros" element={<Registros />} />
      <Route path="/personas" element={<Personas />} />
      <Route path="/auditoria" element={<Auditoria />} />
      <Route path="/digitalizacion" element={<Digitalizacion />} />
      <Route path="/revision-ocr" element={<RevisionOCR />} />
      <Route path="/libros" element={<Libros />} />
      <Route path="/sacramento" element={<Sacramento />} />
      <Route path="/sacramentos" element={<Sacramentos />} />
      <Route path="/usuarios" element={<Usuarios />} />
      <Route path="/reportes" element={<Reportes />} />
      <Route path="/certificados" element={<Certificados />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
