import { Routes, Route, Navigate } from 'react-router-dom'
import PrivateRoute from './components/PrivateRoute'
import { OcrProgressProvider } from './context/OcrProgressContext'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Registros from './pages/Registros'
import Sacramento from './pages/Sacramento'
import Sacramentos from './pages/Sacramentos'
import Personas from './pages/Personas'
import Auditoria from './pages/Auditoria'
import Digitalizacion from './pages/Digitalizacion'
import RevisionOCR from './pages/RevisionOCR'
import Libros from './pages/Libros'
import Usuarios from './pages/Usuarios'
import Reportes from './pages/Reportes'
import Certificados from './pages/Certificados'
import Perfil from './pages/Perfil'

export default function App() {
  return (
    <OcrProgressProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/registros" element={<PrivateRoute><Registros /></PrivateRoute>} />
        <Route path="/sacramento" element={<PrivateRoute><Sacramento /></PrivateRoute>} />
        <Route path="/sacramentos" element={<PrivateRoute><Sacramentos /></PrivateRoute>} />
        <Route path="/personas" element={<PrivateRoute><Personas /></PrivateRoute>} />
        <Route path="/auditoria" element={<PrivateRoute><Auditoria /></PrivateRoute>} />
        <Route path="/digitalizacion" element={<PrivateRoute><Digitalizacion /></PrivateRoute>} />
        <Route path="/revision-ocr" element={<PrivateRoute><RevisionOCR /></PrivateRoute>} />
        <Route path="/libros" element={<PrivateRoute><Libros /></PrivateRoute>} />
        <Route path="/usuarios" element={<PrivateRoute><Usuarios /></PrivateRoute>} />
        <Route path="/reportes" element={<PrivateRoute><Reportes /></PrivateRoute>} />
        <Route path="/certificados" element={<PrivateRoute><Certificados /></PrivateRoute>} />
        <Route path="/perfil" element={<PrivateRoute><Perfil /></PrivateRoute>} />
        
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </OcrProgressProvider>
  )
}
