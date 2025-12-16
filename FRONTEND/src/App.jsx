import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { OcrProgressProvider } from './context/OcrProgressContext'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Sacramento from './pages/Sacramento'
// import Personas from './pages/Personas' // Deshabilitado temporalmente
import Auditoria from './pages/Auditoria'
import Digitalizacion from './pages/Digitalizacion'
import RevisionOCR from './pages/RevisionOCR'
import Libros from './pages/Libros'
import Usuarios from './pages/Usuarios'
import Reportes from './pages/Reportes'
import Estadisticas from './pages/Estadisticas'
import Certificados from './pages/Certificados'
import Sacramentos from './pages/Sacramentos'
import Perfil from './pages/Perfil'

export default function App() {
  return (
    <AuthProvider>
      <OcrProgressProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/sacramento" element={<Sacramento />} />
          <Route path="/sacramentos" element={<Sacramentos />} />
          {/* <Route path="/personas" element={<Personas />} /> */} {/* Deshabilitado temporalmente */}
          <Route path="/auditoria" element={<Auditoria />} />
          <Route path="/digitalizacion" element={<Digitalizacion />} />
          <Route path="/revision-ocr" element={<RevisionOCR />} />
          <Route path="/libros" element={<Libros />} />
          <Route path="/usuarios" element={<Usuarios />} />
          <Route path="/reportes" element={<Reportes />} />
          <Route path="/estadisticas" element={<Estadisticas />} />
          <Route path="/perfil" element={<Perfil />} />
          <Route path="/certificados" element={<Certificados />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </OcrProgressProvider>
    </AuthProvider>
  )
}
