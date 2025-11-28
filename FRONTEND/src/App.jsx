<<<<<<< Updated upstream
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
=======
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './components/PrivateRoute'
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
>>>>>>> Stashed changes

  return (
<<<<<<< Updated upstream
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
=======
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        {/* Rutas protegidas */}
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/registros" element={<PrivateRoute><Registros /></PrivateRoute>} />
        <Route path="/personas" element={<PrivateRoute><Personas /></PrivateRoute>} />
        <Route path="/auditoria" element={<PrivateRoute><Auditoria /></PrivateRoute>} />
        <Route path="/digitalizacion" element={<PrivateRoute><Digitalizacion /></PrivateRoute>} />
        <Route path="/revision-ocr" element={<PrivateRoute><RevisionOCR /></PrivateRoute>} />
        <Route path="/libros" element={<PrivateRoute><Libros /></PrivateRoute>} />
        <Route path="/usuarios" element={<PrivateRoute><Usuarios /></PrivateRoute>} />
        <Route path="/reportes" element={<PrivateRoute><Reportes /></PrivateRoute>} />
        <Route path="/certificados" element={<PrivateRoute><Certificados /></PrivateRoute>} />
        
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
>>>>>>> Stashed changes
  )
}

export default App
