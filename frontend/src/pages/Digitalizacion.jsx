import Layout from '../components/Layout'

export default function Digitalizacion() {
  return (
    <Layout title="Digitalización de Documentos">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Metadatos</h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="sacramento" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Sacramento</label>
                <select id="sacramento" className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent">
                  <option>Seleccione el sacramento</option>
                  <option>Bautizo</option>
                  <option>Confirmación</option>
                  <option>Matrimonio</option>
                  <option>Defunción</option>
                </select>
              </div>
              <div>
                <label htmlFor="libro" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Libro</label>
                <select id="libro" className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent">
                  <option>Seleccione el libro</option>
                </select>
              </div>
              <div>
                <label htmlFor="parroquia" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Parroquia</label>
                <select id="parroquia" className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent">
                  <option>Seleccione la parroquia</option>
                </select>
              </div>
              <div>
                <label htmlFor="provincia" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Provincia</label>
                <select id="provincia" className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent">
                  <option>Seleccione la provincia</option>
                </select>
              </div>
              <div>
                <label htmlFor="ano" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Año</label>
                <select id="ano" className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent">
                  <option>Seleccione el año</option>
                </select>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Preprocesamiento</h3>
            <div className="space-y-3">
              <label className="flex items-center"><input type="checkbox" className="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary" /><span className="ml-3 text-gray-700 dark:text-gray-300">Binarización</span></label>
              <label className="flex items-center"><input type="checkbox" className="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary" /><span className="ml-3 text-gray-700 dark:text-gray-300">Deskew</span></label>
              <label className="flex items-center"><input type="checkbox" className="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary" /><span className="ml-3 text-gray-700 dark:text-gray-300">Denoise</span></label>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Carga de Documentos</h3>
            <div className="flex items-center justify-center w-full">
              <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <span className="material-symbols-outlined text-4xl mb-4 text-gray-500 dark:text-gray-400">cloud_upload</span>
                  <p className="mb-2 text-sm text-gray-500 dark:text-gray-400"><span className="font-semibold">Arrastra y suelta</span> o haz clic para subir</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">PDF, JPG, PNG (MAX. 10MB)</p>
                </div>
                <input id="dropzone-file" type="file" multiple className="hidden" />
              </label>
            </div>
          </div>

          <div className="bg-white dark:bg-background-dark rounded-lg shadow overflow-hidden">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white p-6">Cola de Procesamiento</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                  <tr>
                    <th scope="col" className="px-6 py-3">Documento</th>
                    <th scope="col" className="px-6 py-3">Estado</th>
                    <th scope="col" className="px-6 py-3">Progreso</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                    <th scope="row" className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">Documento 1.pdf</th>
                    <td className="px-6 py-4"><span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">En cola</span></td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700"><div className="bg-yellow-400 h-2.5 rounded-full" style={{ width: '20%' }}></div></div>
                        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">20%</span>
                      </div>
                    </td>
                  </tr>
                  <tr className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                    <th scope="row" className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">Documento 2.pdf</th>
                    <td className="px-6 py-4"><span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-primary/20 dark:text-blue-300">Procesando</span></td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700"><div className="bg-primary h-2.5 rounded-full" style={{ width: '50%' }}></div></div>
                        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">50%</span>
                      </div>
                    </td>
                  </tr>
                  <tr className="bg-white dark:bg-background-dark">
                    <th scope="row" className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">Documento 3.pdf</th>
                    <td className="px-6 py-4"><span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completado</span></td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700"><div className="bg-green-500 h-2.5 rounded-full" style={{ width: '100%' }}></div></div>
                        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">100%</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
