import { useEffect, useState } from 'react'
import Layout from '../components/Layout'

export default function Reportes() {
  const [counts, setCounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/api/v1/reportes/count-by-type')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setCounts(data.counts || [])
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <Layout title="Reportes">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sacramentos por Tipo</h3>
          {loading && <p className="text-sm text-gray-500">Cargando...</p>}
          {error && <p className="text-sm text-red-600">Error: {error}</p>}
          {!loading && !error && (
            <div className="mt-4">
              {counts.length === 0 && <p className="text-sm text-gray-500">No hay datos disponibles.</p>}
              <ul className="space-y-2">
                {counts.map((c) => (
                  <li key={c.tipo} className="flex justify-between items-center border-b py-2">
                    <span className="text-sm text-gray-700 dark:text-gray-200">{c.tipo}</span>
                    <span className="text-lg font-semibold text-gray-900 dark:text-white">{c.total}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Productividad de Digitadores</h3>
          <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">8,765</p>
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <span>2023</span>
            <span className="text-green-500 font-medium">+8%</span>
          </div>
          <div className="mt-4 h-48">
            <svg className="h-full w-full" viewBox="0 0 472 150" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
              <defs>
                <linearGradient id="line-chart-gradient" x1="0" y1="0" x2="0" y2="150" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#0f49bd" stopOpacity="0.3" />
                  <stop offset="1" stopColor="#0f49bd" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path d="M0 109C18.15 109 18.15 21 36.3 21C54.46 21 54.46 41 72.61 41C90.77 41 90.77 93 108.92 93C127.08 93 127.08 33 145.23 33C163.38 33 163.38 101 181.54 101C199.69 101 199.69 61 217.85 61C236 61 236 45 254.15 45C272.31 45 272.31 121 290.46 121C308.62 121 308.62 149 326.77 149C344.92 149 344.92 1 363.08 1C381.23 1 381.23 81 399.38 81C417.54 81 417.54 129 435.69 129C453.85 129 453.85 25 472 25V150H0V109Z" fill="url(#line-chart-gradient)" />
              <path d="M0 109C18.15 109 18.15 21 36.3 21C54.46 21 54.46 41 72.61 41C90.77 41 90.77 93 108.92 93C127.08 93 127.08 33 145.23 33C163.38 33 163.38 101 181.54 101C199.69 101 199.69 61 217.85 61C236 61 236 45 254.15 45C272.31 45 272.31 121 290.46 121C308.62 121 308.62 149 326.77 149C344.92 149 344.92 1 363.08 1C381.23 1 381.23 81 399.38 81C417.54 81 417.54 129 435.69 129C453.85 129 453.85 25 472 25" stroke="#0f49bd" strokeWidth="3" strokeLinecap="round" />
            </svg>
          </div>
        </div>

        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Duplicados Detectados</h3>
          <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">234</p>
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <span>2023</span>
            <span className="text-red-500 font-medium">-5%</span>
          </div>
          <div className="mt-4 h-48 flex items-center justify-center">
            <div className="relative size-40">
              <svg className="size-full" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
                <circle cx="18" cy="18" r="15.915" fill="none" strokeWidth="3" className="stroke-gray-200 dark:stroke-gray-700" />
                <circle cx="18" cy="18" r="15.915" fill="none" strokeWidth="3" strokeDasharray="60, 40" strokeDashoffset="25" strokeLinecap="round" className="stroke-primary" />
                <circle cx="18" cy="18" r="15.915" fill="none" strokeWidth="3" strokeDasharray="30, 70" strokeDashoffset="-15" strokeLinecap="round" className="stroke-yellow-400" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-bold text-gray-900 dark:text-white">35%</span>
                <span className="text-sm text-gray-500 dark:text-gray-400">Resueltos</span>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Errores Más Comunes</h3>
          <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">150</p>
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <span>2023</span>
            <span className="text-green-500 font-medium">+3%</span>
          </div>
          <div className="mt-4 space-y-4">
            {[
              { label: 'Fecha Inválida', pct: 45 },
              { label: 'Nombre Incorrecto', pct: 30 },
              { label: 'Lugar Inconsistente', pct: 15 },
              { label: 'Otros', pct: 10 },
            ].map((row) => (
              <div key={row.label}>
                <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400 mb-1">
                  <span>{row.label}</span>
                  <span>{row.pct}%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className="h-2 rounded-full bg-primary" style={{ width: `${row.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  )
}
