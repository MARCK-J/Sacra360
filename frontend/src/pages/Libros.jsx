import Layout from '../components/Layout'

export default function Libros() {
  return (
    <Layout title="Gestión de Libros">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-card-light dark:bg-card-dark rounded-lg border border-border-light dark:border-border-dark">
            <div className="p-4 border-b border-border-light dark:border-border-dark">
              <h3 className="font-semibold text-lg">Listado de Libros</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-border-light dark:border-border-dark">
                    <th className="p-4 font-medium text-muted-foreground-light dark:text-muted-foreground-dark">Tipo</th>
                    <th className="p-4 font-medium text-muted-foreground-light dark:text-muted-foreground-dark">Número</th>
                    <th className="p-4 font-medium text-muted-foreground-light dark:text-muted-foreground-dark">Rango de Años</th>
                    <th className="p-4 font-medium text-muted-foreground-light dark:text-muted-foreground-dark">Ubicación</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark">
                    <td className="p-4">Bautizo</td>
                    <td className="p-4">1</td>
                    <td className="p-4">2000-2005</td>
                    <td className="p-4 text-muted-foreground-light dark:text-muted-foreground-dark">Sin asignar</td>
                  </tr>
                  <tr className="border-b border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark bg-primary/5">
                    <td className="p-4 font-semibold text-primary">Confirmación</td>
                    <td className="p-4 font-semibold text-primary">2</td>
                    <td className="p-4 font-semibold text-primary">2006-2010</td>
                    <td className="p-4 text-primary">A-1-001</td>
                  </tr>
                  <tr className="border-b border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark">
                    <td className="p-4">Matrimonio</td>
                    <td className="p-4">3</td>
                    <td className="p-4">2011-2015</td>
                    <td className="p-4 text-muted-foreground-light dark:text-muted-foreground-dark">Sin asignar</td>
                  </tr>
                  <tr className="border-b border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark">
                    <td className="p-4">Defunción</td>
                    <td className="p-4">4</td>
                    <td className="p-4">2016-2020</td>
                    <td className="p-4 text-muted-foreground-light dark:text-muted-foreground-dark">Sin asignar</td>
                  </tr>
                  <tr className="hover:bg-background-light dark:hover:bg-background-dark">
                    <td className="p-4">Bautizo</td>
                    <td className="p-4">5</td>
                    <td className="p-4">2021-2023</td>
                    <td className="p-4 text-muted-foreground-light dark:text-muted-foreground-dark">Sin asignar</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div>
          <div className="bg-card-light dark:bg-card-dark rounded-lg border border-border-light dark:border-border-dark p-4">
            <h3 className="font-semibold text-lg mb-4">Asignar Ubicación Física</h3>
            <p className="text-sm text-muted-foreground-light dark:text-muted-foreground-dark mb-4">Seleccionado: Libro de Confirmación #2 (2006-2010)</p>
            <form className="space-y-4">
              <div>
                <label htmlFor="estante" className="block text-sm font-medium mb-1">Estante</label>
                <select id="estante" className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary">
                  <option>Seleccionar estante</option>
                  <option defaultValue> A </option>
                  <option>B</option>
                </select>
              </div>
              <div>
                <label htmlFor="nivel" className="block text-sm font-medium mb-1">Nivel</label>
                <select id="nivel" className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary">
                  <option>Seleccionar nivel</option>
                  <option defaultValue> 1 </option>
                  <option>2</option>
                </select>
              </div>
              <div>
                <label htmlFor="sigla" className="block text-sm font-medium mb-1">Sigla</label>
                <input id="sigla" type="text" defaultValue="001" placeholder="Ingresar sigla" className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <button type="submit" className="w-full bg-primary text-white py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">Guardar Ubicación</button>
            </form>
          </div>
        </div>
        <div className="lg:col-span-3">
          <div className="bg-card-light dark:bg-card-dark rounded-lg border border-border-light dark:border-border-dark p-4">
            <h3 className="font-semibold text-lg mb-4">Cuadrícula de Estanterías</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4">
              <div className="group relative rounded-lg border-2 border-dashed border-border-light dark:border-border-dark flex items-center justify-center cursor-pointer hover:border-primary aspect-square">
                <div className="text-center">
                  <span className="material-symbols-outlined text-4xl text-muted-foreground-light dark:text-muted-foreground-dark group-hover:text-primary">add_box</span>
                  <p className="text-xs mt-1 text-muted-foreground-light dark:text-muted-foreground-dark group-hover:text-primary">Añadir</p>
                </div>
              </div>
              <div className="relative rounded-lg border-2 border-primary bg-primary/10 flex flex-col items-center justify-center p-2 text-center aspect-square">
                <p className="font-bold text-lg text-primary">A-1</p>
                <p className="text-xs text-primary/80">Confirmación #2</p>
              </div>
              {['A-2','A-3','A-4','B-1','B-2','B-3','B-4','C-1','C-2','C-3'].map(key => (
                <div key={key} className="rounded-lg border border-border-light dark:border-border-dark bg-background-light dark:bg-background-dark flex items-center justify-center aspect-square">
                  <p className="font-bold text-lg text-muted-foreground-light dark:text-muted-foreground-dark">{key}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
