import Layout from '../components/Layout'

export default function Certificados() {
  return (
    <Layout title="Generación de Certificados">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-1 space-y-6">
          <div className="bg-white dark:bg-background-dark rounded-lg border border-border-light dark:border-border-dark p-4">
            <h3 className="font-semibold text-lg mb-4">Parámetros</h3>
            <form className="space-y-4">
              <div>
                <label htmlFor="tipo" className="block text-sm font-medium mb-1">Tipo de Sacramento</label>
                <select id="tipo" className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary">
                  <option>Bautizo</option>
                  <option>Confirmación</option>
                  <option>Matrimonio</option>
                  <option>Defunción</option>
                </select>
              </div>
              <div>
                <label htmlFor="persona" className="block text-sm font-medium mb-1">Persona</label>
                <input id="persona" type="text" placeholder="Buscar persona..." className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary" />
                <p className="text-xs text-muted-foreground-light dark:text-muted-foreground-dark mt-1">Sugerencia: escribe nombre y apellido</p>
              </div>
              <div>
                <label htmlFor="libro" className="block text-sm font-medium mb-1">Libro / Foja / Número</label>
                <div className="grid grid-cols-3 gap-2">
                  <input type="text" placeholder="Libro" className="p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary" />
                  <input type="text" placeholder="Foja" className="p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary" />
                  <input type="text" placeholder="Número" className="p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
              </div>
              <div>
                <label htmlFor="plantilla" className="block text-sm font-medium mb-1">Plantilla</label>
                <select id="plantilla" className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary">
                  <option>Certificado Simple</option>
                  <option>Certificado con Anotaciones</option>
                  <option>Certificado Internacional</option>
                </select>
              </div>
              <div>
                <label htmlFor="idioma" className="block text-sm font-medium mb-1">Idioma</label>
                <select id="idioma" className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary">
                  <option>Español</option>
                  <option>Inglés</option>
                </select>
              </div>
              <div>
                <label htmlFor="observaciones" className="block text-sm font-medium mb-1">Observaciones</label>
                <textarea id="observaciones" rows={3} placeholder="Notas o aclaraciones opcionales" className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <div className="grid grid-cols-2 gap-3 pt-2">
                <button type="button" className="px-3 py-2 rounded-lg border border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark">Previsualizar</button>
                <button type="button" className="px-3 py-2 rounded-lg bg-primary text-white hover:bg-primary/90">Generar</button>
              </div>
            </form>
          </div>

          <div className="bg-white dark:bg-background-dark rounded-lg border border-border-light dark:border-border-dark p-4">
            <h4 className="font-semibold mb-2">Metadatos</h4>
            <ul className="text-sm space-y-1 text-muted-foreground-light dark:text-muted-foreground-dark">
              <li>Responsable: Admin</li>
              <li>Fecha: 2024-03-21</li>
              <li>Parroquia: N. Sra. de la Paz</li>
            </ul>
          </div>
        </section>

        <section className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-background-dark rounded-lg border border-border-light dark:border-border-dark p-6">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-xl font-bold">Vista Previa</h3>
              <div className="flex gap-2">
                <button className="px-3 py-2 rounded-lg border border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark">Imprimir</button>
                <button className="px-3 py-2 rounded-lg bg-primary text-white hover:bg-primary/90">Exportar PDF</button>
              </div>
            </div>
            <div className="rounded-lg border border-dashed border-border-light dark:border-border-dark p-6 bg-background-light dark:bg-background-dark">
              <div className="max-w-3xl mx-auto bg-white dark:bg-gray-900 rounded-lg shadow p-8">
                <div className="text-center mb-6">
                  <h4 className="text-2xl font-extrabold">Certificado de Bautizo</h4>
                  <p className="text-sm text-muted-foreground-light dark:text-muted-foreground-dark">Parroquia Nuestra Señora de la Paz</p>
                </div>
                <div className="space-y-3 text-sm">
                  <p><span className="font-semibold">Nombre:</span> Sofía Rodríguez</p>
                  <p><span className="font-semibold">Padres:</span> Manuel Rodríguez y Laura García</p>
                  <p><span className="font-semibold">Fecha de Bautizo:</span> 2020-03-15</p>
                  <p><span className="font-semibold">Ministro:</span> Pbro. Juan Pérez</p>
                  <p><span className="font-semibold">Libro / Foja / Nº:</span> 5 / 12 / 123</p>
                </div>
                <div className="mt-6 flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground-light dark:text-muted-foreground-dark">Emitido por: Admin</p>
                    <p className="text-xs text-muted-foreground-light dark:text-muted-foreground-dark">Fecha: 2024-03-21</p>
                  </div>
                  <div className="text-center">
                    <div className="h-12 w-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto">
                      <span className="material-symbols-outlined">workspace_premium</span>
                    </div>
                    <p className="text-xs mt-1">Sello Parroquial</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-background-dark rounded-lg border border-border-light dark:border-border-dark p-6">
            <h3 className="text-lg font-semibold mb-4">Certificados Recientes</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-3">Persona</th>
                    <th className="px-6 py-3">Sacramento</th>
                    <th className="px-6 py-3">Fecha</th>
                    <th className="px-6 py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { p: 'Sofía Rodríguez', t: 'Bautizo', f: '2024-03-21' },
                    { p: 'Carlos López', t: 'Confirmación', f: '2024-03-18' },
                    { p: 'Ana García', t: 'Matrimonio', f: '2024-03-15' },
                  ].map((r) => (
                    <tr key={r.p} className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                      <td className="px-6 py-3 font-medium text-gray-900 dark:text-white whitespace-nowrap">{r.p}</td>
                      <td className="px-6 py-3">{r.t}</td>
                      <td className="px-6 py-3">{r.f}</td>
                      <td className="px-6 py-3">
                        <button className="px-3 py-1 rounded border border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark mr-2">Ver</button>
                        <button className="px-3 py-1 rounded bg-primary text-white hover:bg-primary/90">Reimprimir</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  )
}
