import Layout from '../components/Layout'
import PermissionGuard from '../components/PermissionGuard'

export default function Registros() {
  return (
    <Layout title="Gestión de Registros">
      <div className="bg-white dark:bg-gray-900/50 rounded-lg shadow">
        <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-800">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="relative w-full sm:w-72">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">search</span>
              <input className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary" placeholder="Buscar por persona, sacramento..." type="text" />
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <select className="form-select border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary">
                <option>Año</option><option>2023</option><option>2022</option><option>2021</option>
              </select>
              <select className="form-select border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary">
                <option>Parroquia</option>
              </select>
              <select className="form-select border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary">
                <option>Libro</option>
              </select>
              <input className="form-input border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary" placeholder="Apellido" type="text" />
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-6 py-3" scope="col">Persona</th>
                <th className="px-6 py-3" scope="col">Sacramento</th>
                <th className="px-6 py-3" scope="col">Año</th>
                <th className="px-6 py-3" scope="col">Estado</th>
                <th className="px-6 py-3 text-center" scope="col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr className="bg-white dark:bg-gray-900/50 border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <th className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap" scope="row">Sofía Rodríguez</th>
                <td className="px-6 py-4">Bautizo</td>
                <td className="px-6 py-4">2020</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completado</span>
                </td>
                <td className="px-6 py-4 text-center space-x-2">
                  <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">visibility</span></button>
                  <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">edit</span></button>
                  <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">draft</span></button>
                  <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">gavel</span></button>
                </td>
              </tr>
              <tr className="bg-white dark:bg-gray-900/50 border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <th className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap" scope="row">Carlos López</th>
                <td className="px-6 py-4">Confirmación</td>
                <td className="px-6 py-4">2021</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">Pendiente</span>
                </td>
                <td className="px-6 py-4 text-center space-x-2">
                  <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">visibility</span></button>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">edit</span></button>
                  </PermissionGuard>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">draft</span></button>
                  </PermissionGuard>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">gavel</span></button>
                  </PermissionGuard>
                </td>
              </tr>
              <tr className="bg-white dark:bg-gray-900/50 border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <th className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap" scope="row">Ana García</th>
                <td className="px-6 py-4">Matrimonio</td>
                <td className="px-6 py-4">2022</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completado</span>
                </td>
                <td className="px-6 py-4 text-center space-x-2">
                  <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">visibility</span></button>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">edit</span></button>
                  </PermissionGuard>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">draft</span></button>
                  </PermissionGuard>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">gavel</span></button>
                  </PermissionGuard>
                </td>
              </tr>
              <tr className="bg-white dark:bg-gray-900/50 border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <th className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap" scope="row">Diego Martínez</th>
                <td className="px-6 py-4">Defunción</td>
                <td className="px-6 py-4">2023</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completado</span>
                </td>
                <td className="px-6 py-4 text-center space-x-2">
                  <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">visibility</span></button>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">edit</span></button>
                  </PermissionGuard>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">draft</span></button>
                  </PermissionGuard>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">gavel</span></button>
                  </PermissionGuard>
                </td>
              </tr>
              <tr className="bg-white dark:bg-gray-900/50 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <th className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap" scope="row">Isabel Pérez</th>
                <td className="px-6 py-4">Bautizo</td>
                <td className="px-6 py-4">2020</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completado</span>
                </td>
                <td className="px-6 py-4 text-center space-x-2">
                  <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">visibility</span></button>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">edit</span></button>
                  </PermissionGuard>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">draft</span></button>
                  </PermissionGuard>
                  <PermissionGuard module="registros" action="update">
                    <button className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">gavel</span></button>
                  </PermissionGuard>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-gray-200 dark:border-gray-800 flex items-center justify-between">
          <span className="text-sm text-gray-700 dark:text-gray-400">Mostrando 1 a 5 de 100 registros</span>
          <div className="inline-flex rounded-lg shadow-sm">
            <button className="px-3 py-1 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-l-lg hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700">Anterior</button>
            <button className="px-3 py-1 text-sm font-medium text-gray-500 bg-white border-t border-b border-gray-300 hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700">1</button>
            <button className="px-3 py-1 text-sm font-medium text-gray-500 bg-white border-t border-b border-gray-300 hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700">2</button>
            <button className="px-3 py-1 text-sm font-medium text-gray-500 bg-white border-t border-b border-gray-300 hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700">3</button>
            <button className="px-3 py-1 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-r-lg hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700">Siguiente</button>
          </div>
        </div>
      </div>
    </Layout>
  )
}
