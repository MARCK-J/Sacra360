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
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Historial de Sacramentos</h3>
        </div>
        <div className="p-6">
          <p className="text-sm text-gray-600">Use la página de <strong>Sacramento</strong> para crear nuevos registros de sacramentos.</p>
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
            </tbody>
          </table>
        </div>
      </div>

      <DuplicatesMergeModal open={mergeOpen} onClose={() => setMergeOpen(false)} />
    </Layout>
  )
}
