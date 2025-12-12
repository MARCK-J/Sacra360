import Layout from '../components/Layout'
import { useCallback, useEffect, useState } from 'react'

export default function Certificados() {
  const [sacramentos, setSacramentos] = useState([])
  const [loadingList, setLoadingList] = useState(false)
  const [errorList, setErrorList] = useState(null)
  const [selected, setSelected] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadSacramentos()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function loadSacramentos() {
    setLoadingList(true)
    setErrorList(null)
    try {
      const res = await fetch('/api/v1/sacramentos/?limit=20')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      const list = Array.isArray(data) ? data : (data.sacramentos || data || [])
      setSacramentos(list)
      if (list.length > 0 && !selected) setSelected(list[0])
    } catch (err) {
      setErrorList(String(err))
    } finally {
      setLoadingList(false)
    }
  }
  const handlePrint = useCallback((elementId) => {
    const el = document.getElementById(elementId)
    if (!el) return alert('Preview no disponible para imprimir')
    const content = el.innerHTML
    const win = window.open('', '_blank', 'toolbar=0,location=0,menubar=0')
    if (!win) return alert('No se pudo abrir la ventana de impresión')
    const style = `
      <style>
        @page { size: A4; margin: 20mm; }
        body { font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; color: #111827; }
        .certificate-container { width: 100%; }
        .text-center { text-align: center; }
        .mb-6 { margin-bottom: 1.5rem; }
        .p-8 { padding: 2rem; }
        .font-extrabold { font-weight: 800; }
        .text-2xl { font-size: 1.5rem; }
        .text-sm { font-size: .875rem; }
        .mt-6 { margin-top: 1.5rem; }
      </style>
    `
    win.document.open()
    win.document.write(`<!doctype html><html><head><title>Certificado</title>${style}</head><body><div class="certificate-container">${content}</div></body></html>`)
    win.document.close()
    // Wait for images/fonts to load
    win.focus()
    setTimeout(() => {
      try {
        win.print()
      } catch (e) {
        console.error(e)
        alert('Error al intentar imprimir/exportar. Usa la opción de imprimir del navegador.')
      }
    }, 400)
  }, [])

  const handleExportPDF = useCallback((elementId) => {
    const generateAndDownload = async () => {
      let html2canvas = null
      let jsPDF = null
      try {
        const modCanvas = await import('html2canvas')
        html2canvas = modCanvas.default || modCanvas
        const modPdf = await import('jspdf')
        jsPDF = modPdf.jsPDF || modPdf.default || modPdf
      } catch (err) {
        // dynamic import failed — fall back to print dialog
        console.warn('PDF libs not available, falling back to print dialog', err)
        return handlePrint(elementId)
      }

      const el = document.getElementById(elementId)
      if (!el) return alert('Preview no disponible para exportar')
      const originalBg = el.style.backgroundColor
      el.style.backgroundColor = '#ffffff'
      try {
        // ensure web fonts have loaded so canvas text matches on-screen
        try { if (document.fonts && document.fonts.ready) await document.fonts.ready } catch (e) {}
        const canvas = await html2canvas(el, { scale: 2, useCORS: true, backgroundColor: '#ffffff' })
        const pdf = new jsPDF('p', 'mm', 'a4')
        const pdfWidth = pdf.internal.pageSize.getWidth()
        const pdfHeight = pdf.internal.pageSize.getHeight()

        const canvasWidth = canvas.width
        const canvasHeight = canvas.height
        const pageHeightPx = Math.floor(canvasWidth * (pdfHeight / pdfWidth))

        let position = 0
        while (position < canvasHeight) {
          const sliceHeight = Math.min(pageHeightPx, canvasHeight - position)
          const pageCanvas = document.createElement('canvas')
          pageCanvas.width = canvasWidth
          pageCanvas.height = sliceHeight
          const ctx = pageCanvas.getContext('2d')
          ctx.drawImage(canvas, 0, position, canvasWidth, sliceHeight, 0, 0, canvasWidth, sliceHeight)
          const pageImgData = pageCanvas.toDataURL('image/png')
          const pageHeightMm = (sliceHeight * pdfWidth) / canvasWidth
          pdf.addImage(pageImgData, 'PNG', 0, 0, pdfWidth, pageHeightMm)
          position += sliceHeight
          if (position < canvasHeight) pdf.addPage()
        }

        const filename = `certificado-${Date.now()}.pdf`
        pdf.save(filename)
      } catch (err) {
        console.error('PDF export error', err)
        alert('Error al generar PDF. Se abrirá el diálogo de impresión como respaldo.')
        handlePrint(elementId)
      } finally {
        el.style.backgroundColor = originalBg
      }
    }
    generateAndDownload()
  }, [handlePrint])
  function getRowClass(r) {
    const selId = selected && (selected.id_sacramento || selected.id)
    const rowId = r && (r.id_sacramento || r.id)
    return selId && rowId && selId === rowId ? 'bg-primary/5' : ''
  }

  // Map tipo identifiers (id or numeric string) to human-friendly labels
  const TIPO_MAP = {
    1: 'bautizo',
    2: 'confirmacion',
    3: 'matrimonio',
    4: 'defuncion',
    5: 'primera comunion'
  }

  function getTipoLabel(item) {
    if (!item) return '-'
    const rawTipo = item.tipo_nombre || item.tipo_sacramento || item.tipo || item.tipo_id || item.tipoId
    if (!rawTipo) return '-'
    const s = String(rawTipo)
    // If it's purely numeric (e.g. '4'), prefer mapping via number
    let label = ''
    if (/^\d+$/.test(s)) {
      const n = Number(s)
      label = TIPO_MAP[n] || `Tipo ${n}`
    } else {
      label = s
    }
    // Capitalize first letter for display
    return label && typeof label === 'string' ? `${label.charAt(0).toUpperCase()}${label.slice(1)}` : label
  }

  // Client-side filtered list by persona name (simple substring match)
  const filteredSacramentos = sacramentos.filter((r) => {
    if (!searchTerm || String(searchTerm).trim() === '') return true
    const name = (r.persona_nombre || r.person_name || r.persona_id || '')
    return String(name).toLowerCase().includes(String(searchTerm).toLowerCase())
  })

  return (
    <Layout title="Generación de Certificados">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-1 space-y-6">
          <div className="bg-white dark:bg-background-dark rounded-lg border border-border-light dark:border-border-dark p-4">
            <h3 className="font-semibold text-lg mb-4">Parámetros</h3>
            <form className="space-y-4">
              <div>
                <label htmlFor="persona" className="block text-sm font-medium mb-1">Buscar Persona</label>
                <input
                  id="persona"
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Escribe nombre o apellido para filtrar..."
                  className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <p className="text-xs text-muted-foreground-light dark:text-muted-foreground-dark mt-1">Filtra la lista de certificados por nombre de la persona.</p>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-2">
                <button type="button" onClick={() => { setSearchTerm(''); loadSacramentos() }} className="px-3 py-2 rounded-lg border border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark">Refrescar</button>
                <div />
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
                <button onClick={() => handlePrint('certificate-preview')} className="px-3 py-2 rounded-lg border border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark">Imprimir</button>
                <button onClick={() => handleExportPDF('certificate-preview')} className="px-3 py-2 rounded-lg bg-primary text-white hover:bg-primary/90">Exportar PDF</button>
              </div>
            </div>
            <div className="rounded-lg border border-dashed border-border-light dark:border-border-dark p-6 bg-background-light dark:bg-background-dark">
              <div id="certificate-preview" className="max-w-3xl mx-auto bg-white dark:bg-gray-900 rounded-lg shadow p-8">
                {selected ? (
                  <div>
                    <div className="text-center mb-6">
                      <h4 className="text-2xl font-extrabold">Certificado de {getTipoLabel(selected)}</h4>
                      <p className="text-sm text-muted-foreground-light dark:text-muted-foreground-dark">{selected.institucion_nombre || selected.sacrament_location || selected.institucion || 'Parroquia'}</p>
                    </div>
                    <div className="space-y-3 text-sm">
                      <p><span className="font-semibold">Nombre:</span> {selected.persona_nombre ?? selected.persona_id ?? selected.person_name ?? '-'}</p>
                      <p><span className="font-semibold">Padres:</span> {
                        selected.padres
                        || ((selected.nombre_padre || selected.persona_padre || selected.padre || selected.father_name) || (selected.nombre_madre || selected.persona_madre || selected.madre || selected.mother_name))
                          ? `${selected.nombre_padre || selected.persona_padre || selected.padre || selected.father_name} y ${selected.nombre_madre || selected.persona_madre || selected.madre || selected.mother_name}`
                          : '-'
                      }</p>
                      <p><span className="font-semibold">Fecha:</span> {selected.fecha_sacramento?.substring(0,10) || selected.fecha || '-'}</p>
                      <p><span className="font-semibold">Ministro:</span> {selected.ministro || selected.sacrament_minister || selected.ministro_bautizo || selected.ministro_confirmacion || '-'}</p>
                      <p><span className="font-semibold">Libro / Foja / Nº:</span> {`${selected.libro_nombre || selected.libro || selected.libro_acta || (selected.libro_id ? `Libro ${selected.libro_id}` : '-')} / ${selected.foja || selected.folio || '-'} / ${selected.numero_acta || selected.numero || '-'}`}</p>
                    </div>
                    <div className="mt-6 flex items-center justify-between">
                      <div>
                        <p className="text-xs text-muted-foreground-light dark:text-muted-foreground-dark">Emitido por: Admin</p>
                        <p className="text-xs text-muted-foreground-light dark:text-muted-foreground-dark">Fecha: {new Date().toISOString().substring(0,10)}</p>
                      </div>
                      <div className="text-center">
                        <div className="h-12 w-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto">
                          <span className="material-symbols-outlined">workspace_premium</span>
                        </div>
                        <p className="text-xs mt-1">Sello Parroquial</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-sm text-gray-500 py-8">No hay registro seleccionado</div>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-background-dark rounded-lg border border-border-light dark:border-border-dark p-6">
            <h3 className="text-lg font-semibold mb-4">Certificados Recientes</h3>
            {loadingList ? (
              <p className="text-sm text-gray-500">Cargando...</p>
            ) : errorList ? (
              <p className="text-sm text-red-600">Error: {errorList}</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                  <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700/50">
                    <tr>
                      <th className="px-6 py-3">ID</th>
                      <th className="px-6 py-3">Persona</th>
                      <th className="px-6 py-3">Sacramento</th>
                      <th className="px-6 py-3">Fecha</th>
                      <th className="px-6 py-3">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSacramentos.map((r) => (
                      <tr key={r.id_sacramento || r.id} className={`bg-white dark:bg-background-dark border-b dark:border-gray-700 ${getRowClass(r)}`}>
                        <td className="px-6 py-3 font-medium text-gray-900 dark:text-white whitespace-nowrap">{r.id_sacramento || r.id}</td>
                        <td className="px-6 py-3">{r.persona_nombre ?? r.persona_id ?? r.person_name}</td>
                        <td className="px-6 py-3">{getTipoLabel(r)}</td>
                        <td className="px-6 py-3">{r.fecha_sacramento?.substring(0,10) || r.fecha}</td>
                        <td className="px-6 py-3">
                          <button onClick={() => setSelected(r)} className="px-3 py-1 rounded border border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark mr-2">Ver</button>
                          <button onClick={() => { setSelected(r); handlePrint('certificate-preview') }} className="px-3 py-1 rounded bg-primary text-white hover:bg-primary/90">Reimprimir</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      </div>
    </Layout>
  )
}
