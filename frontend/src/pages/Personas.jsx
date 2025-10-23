import { useState } from 'react'
import Layout from '../components/Layout'
import DuplicatesMergeModal from '../components/DuplicatesMergeModal'
export default function Personas() {
  const [mergeOpen, setMergeOpen] = useState(false)
  return (
    <Layout title="Gestión de Personas">
            <div className="bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200 dark:border-gray-800">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Datos Personales</h3>
              </div>
              <form className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="nombres">Nombres</label>
                    <input className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="nombres" placeholder="Ingrese los nombres" type="text" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="apellidos">Apellidos</label>
                    <input className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="apellidos" placeholder="Ingrese los apellidos" type="text" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="fecha-nacimiento">Fecha de Nacimiento</label>
                    <input className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="fecha-nacimiento" type="date" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="lugar-nacimiento">Lugar de Nacimiento</label>
                    <input className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="lugar-nacimiento" placeholder="Ingrese el lugar" type="text" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="padre">Padre</label>
                    <input className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="padre" placeholder="Ingrese el nombre del padre" type="text" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="madre">Madre</label>
                    <input className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="madre" placeholder="Ingrese el nombre de la madre" type="text" />
                  </div>
                </div>
        </form>
      </div>
      <div className="mt-8 bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sacramentos Vinculados</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                  <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700/50 dark:text-gray-400">
                    <tr>
                      <th className="px-6 py-3" scope="col">Sacramento</th>
                      <th className="px-6 py-3" scope="col">Fecha</th>
                      <th className="px-6 py-3" scope="col">Lugar</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="bg-white dark:bg-background-dark/50 border-b dark:border-gray-700">
                      <th className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" scope="row">Bautizo</th>
                      <td className="px-6 py-4">2000-05-15</td>
                      <td className="px-6 py-4">Parroquia San Juan</td>
                    </tr>
                    <tr className="bg-white dark:bg-background-dark/50 border-b dark:border-gray-700">
                      <th className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" scope="row">Confirmación</th>
                      <td className="px-6 py-4">2015-08-20</td>
                      <td className="px-6 py-4">Catedral Metropolitana</td>
                    </tr>
                    <tr className="bg-white dark:bg-background-dark/50">
                      <th className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" scope="row">Matrimonio</th>
                      <td className="px-6 py-4">2025-03-10</td>
                      <td className="px-6 py-4">Iglesia del Carmen</td>
                    </tr>
                  </tbody>
          </table>
        </div>
      </div>
      <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 dark:border-yellow-500 p-4 rounded-r-lg">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="material-symbols-outlined text-yellow-400 dark:text-yellow-500">warning</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">Posibles Duplicados Encontrados</h3>
            <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
              <div className="flex items-center gap-4 mt-4">
                <div className="w-12 h-12 rounded-full bg-cover bg-center" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDYcBTrXWIsdp2l4-8KgVeJrDD4QEZ7LPp0U7mjXdAwrHKy_-V2iA4bzeWeTeGeJku_p9REbThgyunAwGsRm7FEtyeCNBmm_t9lFI3HwsBuleTrxnAitLPCQ1dMSyUwlmDRMZlql2CNwWKWLYn1qh_x5p5tiR7SmRttj7HjE6B1CIJxLmJWClIK2oVyjmPNnArv-9ZZ05LRffM3CUVcaFKfoxabNulrEF4HduPEmi06095SIcsfKEXUexAK5YzJtnyzTX3ZZZZBnG0")' }} />
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">Carlos Mendoza</p>
                  <p className="text-gray-600 dark:text-gray-400">Fecha de Nacimiento: 1990-01-10</p>
                </div>
                <button className="ml-auto px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary" onClick={() => setMergeOpen(true)}>
                  Fusionar Registros
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <DuplicatesMergeModal open={mergeOpen} onClose={() => setMergeOpen(false)} />
    </Layout>
  )
}
