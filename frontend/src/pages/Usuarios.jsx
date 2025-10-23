import Layout from '../components/Layout'

export default function Usuarios() {
  return (
    <Layout title="Gestión de Usuarios">
      <div className="space-y-8">
        <div className="bg-white dark:bg-background-dark p-6 rounded-xl shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
              <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th scope="col" className="px-6 py-3">Nombre</th>
                  <th scope="col" className="px-6 py-3">Email</th>
                  <th scope="col" className="px-6 py-3">Rol</th>
                  <th scope="col" className="px-6 py-3">Estado</th>
                  <th scope="col" className="px-6 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                  <td className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">Carlos Mendoza</td>
                  <td className="px-6 py-4">carlos.mendoza@example.com</td>
                  <td className="px-6 py-4"><span className="bg-primary/10 text-primary text-xs font-medium px-2.5 py-0.5 rounded-full">Administrador</span></td>
                  <td className="px-6 py-4"><span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 text-xs font-medium px-2.5 py-0.5 rounded-full">Activo</span></td>
                  <td className="px-6 py-4 text-right"><button className="font-medium text-primary hover:underline">Editar</button></td>
                </tr>
                <tr className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                  <td className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">Ana Rodriguez</td>
                  <td className="px-6 py-4">ana.rodriguez@example.com</td>
                  <td className="px-6 py-4"><span className="bg-primary/10 text-primary text-xs font-medium px-2.5 py-0.5 rounded-full">Digitalizador</span></td>
                  <td className="px-6 py-4"><span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 text-xs font-medium px-2.5 py-0.5 rounded-full">Activo</span></td>
                  <td className="px-6 py-4 text-right"><button className="font-medium text-primary hover:underline">Editar</button></td>
                </tr>
                <tr className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                  <td className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">Luis Perez</td>
                  <td className="px-6 py-4">luis.perez@example.com</td>
                  <td className="px-6 py-4"><span className="bg-primary/10 text-primary text-xs font-medium px-2.5 py-0.5 rounded-full">Revisor</span></td>
                  <td className="px-6 py-4"><span className="bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300 text-xs font-medium px-2.5 py-0.5 rounded-full">Inactivo</span></td>
                  <td className="px-6 py-4 text-right"><button className="font-medium text-primary hover:underline">Editar</button></td>
                </tr>
                <tr className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                  <td className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">Sofia Gomez</td>
                  <td className="px-6 py-4">sofia.gomez@example.com</td>
                  <td className="px-6 py-4"><span className="bg-primary/10 text-primary text-xs font-medium px-2.5 py-0.5 rounded-full">Consultor</span></td>
                  <td className="px-6 py-4"><span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 text-xs font-medium px-2.5 py-0.5 rounded-full">Activo</span></td>
                  <td className="px-6 py-4 text-right"><button className="font-medium text-primary hover:underline">Editar</button></td>
                </tr>
                <tr className="bg-white dark:bg-background-dark">
                  <td className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">Javier Torres</td>
                  <td className="px-6 py-4">javier.torres@example.com</td>
                  <td className="px-6 py-4"><span className="bg-primary/10 text-primary text-xs font-medium px-2.5 py-0.5 rounded-full">Administrador</span></td>
                  <td className="px-6 py-4"><span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 text-xs font-medium px-2.5 py-0.5 rounded-full">Activo</span></td>
                  <td className="px-6 py-4 text-right"><button className="font-medium text-primary hover:underline">Editar</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-background-dark p-6 rounded-xl shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Editar Usuario</h3>
            <form className="space-y-4">
              <div>
                <label htmlFor="name" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">Nombre</label>
                <input id="name" type="text" defaultValue="Carlos Mendoza" className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5" />
              </div>
              <div>
                <label htmlFor="email" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">Email</label>
                <input id="email" type="email" defaultValue="carlos.mendoza@example.com" className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5" />
              </div>
              <div>
                <label htmlFor="role" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">Rol</label>
                <select id="role" className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5">
                  <option defaultValue>Administrador</option>
                  <option value="DG">Digitalizador</option>
                  <option value="RV">Revisor</option>
                  <option value="CN">Consultor</option>
                </select>
              </div>
              <div>
                <label htmlFor="status" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">Estado</label>
                <select id="status" className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5">
                  <option defaultValue>Activo</option>
                  <option value="IN">Inactivo</option>
                </select>
              </div>
            </form>
          </div>

          <div className="bg-white dark:bg-background-dark p-6 rounded-xl shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Permisos</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th scope="col" className="px-4 py-3">Módulo</th>
                    <th scope="col" className="px-2 py-3 text-center">Crear</th>
                    <th scope="col" className="px-2 py-3 text-center">Leer</th>
                    <th scope="col" className="px-2 py-3 text-center">Actualizar</th>
                    <th scope="col" className="px-2 py-3 text-center">Eliminar</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { modulo: 'Digitalización', c: true, r: true, u: true, d: false },
                    { modulo: 'Revisión OCR', c: false, r: true, u: true, d: false },
                    { modulo: 'Registros', c: true, r: true, u: true, d: true },
                    { modulo: 'Personas', c: false, r: true, u: true, d: false },
                    { modulo: 'Libros', c: false, r: true, u: false, d: false },
                  ].map((row) => (
                    <tr key={row.modulo} className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                      <td className="px-4 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">{row.modulo}</td>
                      {['c','r','u','d'].map((k) => (
                        <td key={k} className="px-2 py-4 text-center">
                          <input type="checkbox" defaultChecked={row[k]} className="form-checkbox h-5 w-5 text-primary bg-gray-100 border-gray-300 rounded focus:ring-primary dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600" />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-4">
          <button className="px-6 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600">Cancelar</button>
          <button className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">Guardar Cambios</button>
        </div>
      </div>
    </Layout>
  )
}
