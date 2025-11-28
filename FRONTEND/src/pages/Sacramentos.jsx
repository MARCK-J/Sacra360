import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

const API_URL = 'http://localhost:8002/api/v1'

export default function Sacramentos() {
  const [sacramentos, setSacramentos] = useState([])
  const [loading, setLoading] = useState(false)
  const [filtros, setFiltros] = useState({
    tipo: '',
    persona: '',
    fecha_desde: '',
    fecha_hasta: ''
  })

  useEffect(() => {
    cargarSacramentos()
  }, [])

  const cargarSacramentos = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/sacramentos`)
      const data = await res.json()
      setSacramentos(data)
    } catch (err) {
      console.error('Error cargando sacramentos:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout title="Sacramentos Registrados">
      <div className="bg-white dark:bg-gray-900/50 rounded-lg shadow">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Lista de Sacramentos
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Consulta y gestiona los sacramentos registrados en el sistema
          </p>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando sacramentos...</p>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400">
                Próximamente: Vista de sacramentos registrados con filtros y búsqueda
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                Total de registros: {sacramentos.length}
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
