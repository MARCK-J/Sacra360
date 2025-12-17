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
    // If URL contains ?id=..., load that sacramento and set as selected (useful after creating)
    try {
      const params = new URLSearchParams(window.location.search)
      const idParam = params.get('id')
      if (idParam) {
        ;(async () => {
          try {
            const r = await fetch(`/api/v1/sacramentos/${idParam}`)
            if (r.ok) {
              const d = await r.json()
              setSelected(d)
            }
          } catch (e) {
            // ignore
          }
        })()
      }
    } catch (e) {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function loadSacramentos() {
    setLoadingList(true)
    setErrorList(null)
    try {
      // Use reportes endpoint which returns persona/tipo/institucion details
      const res = await fetch('/api/v1/reportes/sacramentos?page=1&limit=20')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      const list = Array.isArray(data) ? data : (data.sacramentos || data || [])
      setSacramentos(list)
      if (list.length > 0 && !selected) {
        const first = list[0]
        const id = first.id_sacramento || first.id
        // fetch assembled certificado to get libro_nombre, padres, padrinos
        try {
          const r = await fetch(`/api/v1/certificados/${id}`)
          if (r.ok) {
            const d = await r.json()
            setSelected(d)
          } else {
            setSelected(first)
          }
        } catch (e) {
          setSelected(first)
        }
      }
    } catch (err) {
      setErrorList(String(err))
    } finally {
      setLoadingList(false)
    }
  }
  // Shared CSS for printed/exported certificates (without <style> wrapper)
  const CERT_CSS = `
        @page { size: A4; margin: 18mm; }
        :root{ --paper-bg: #f9fafb; --accent:#0b74ff; --muted:#6b7280; }
        body { font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; color: #0f172a; background: var(--paper-bg); padding: 12px; }
        .certificate-wrapper{ max-width: 900px; margin: 0 auto; }
        .certificate { background: #ffffff; border-radius: 12px; padding: 36px; box-shadow: 0 6px 20px rgba(15,23,42,0.06); border: 1px solid rgba(15,23,42,0.04); }
        .cert-header { text-align: center; margin-bottom: 18px; }
        .cert-title { font-weight: 800; font-size: 26px; letter-spacing: -0.02em; }
        .cert-sub { color: var(--muted); font-size: 12px; margin-top: 4px; }
        .cert-body { display: grid; grid-template-columns: 1fr; gap: 12px; margin-top: 12px; font-size: 15px; }
        .field-label{ font-weight:600; display:inline-block; width:120px }
        .contrayentes { display:flex; gap:18px; align-items:flex-start }
        .spouse { flex:1; background:#fafafa; padding:10px; border-radius:8px; border:1px solid rgba(15,23,42,0.03) }
        .footer { display:flex; justify-content:space-between; align-items:center; margin-top:20px }
        .issuer { color:var(--muted); font-size:12px }
        .seal { text-align:center }
        .book-line{ color:var(--muted); font-size:14px }
        @media print{
          body { background: white; padding:0 }
          .certificate { box-shadow: none; border: none; border-radius: 0; padding: 18mm }
        }
  `
  const handlePrint = useCallback((elementId) => {
    const el = document.getElementById(elementId)
    if (!el) return alert('Preview no disponible para imprimir')
    const content = el.innerHTML
    const win = window.open('', '_blank', 'toolbar=0,location=0,menubar=0')
    if (!win) return alert('No se pudo abrir la ventana de impresión')
    const style = `<style>${CERT_CSS}</style>`
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
      // Ensure certificate CSS is present in the current document so exported PDF matches print template
      let injectedStyle = null
      let addedStyle = false
      try {
        injectedStyle = document.getElementById('cert-style')
        if (!injectedStyle) {
          injectedStyle = document.createElement('style')
          injectedStyle.id = 'cert-style'
          injectedStyle.innerHTML = CERT_CSS
          document.head.appendChild(injectedStyle)
          addedStyle = true
        }
      } catch (e) {
        // ignore injection errors
      }
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
        // remove injected style if we added it
        try {
          if (addedStyle && injectedStyle && injectedStyle.parentNode) injectedStyle.parentNode.removeChild(injectedStyle)
        } catch (e) {}
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
    // rawTipo may be a primitive (id or name) or an object { id_tipo, nombre }
    let rawTipo = item.tipo || item.tipo_nombre || item.tipo_sacramento || item.tipo_id || item.tipoId
    if (rawTipo && typeof rawTipo === 'object') {
      const name = rawTipo.nombre || rawTipo.name || rawTipo.tipo || rawTipo.nombre_tipo
      if (name != null && String(name).trim() !== '') {
        const sName = String(name).trim()
        // If the backend stored a numeric value in the nombre field, map it to a label
        if (/^\d+$/.test(sName)) {
          const n = Number(sName)
          const mapped = TIPO_MAP[n] || `Tipo ${n}`
          return `${mapped.charAt(0).toUpperCase()}${mapped.slice(1)}`
        }
        return `${sName.charAt(0).toUpperCase()}${sName.slice(1)}`
      }
      const id = rawTipo.id_tipo || rawTipo.id || rawTipo.tipo_id
      if (id != null) {
        const n = Number(id)
        const m = TIPO_MAP[n]
        const label = m || `Tipo ${n}`
        return `${label.charAt(0).toUpperCase()}${label.slice(1)}`
      }
      return '-'
    }
    if (rawTipo == null) return '-'
    const s = String(rawTipo).trim()
    if (s === '') return '-'
    if (/^\d+$/.test(s)) {
      const n = Number(s)
      const label = TIPO_MAP[n] || `Tipo ${n}`
      return `${label.charAt(0).toUpperCase()}${label.slice(1)}`
    }
    return `${s.charAt(0).toUpperCase()}${s.slice(1)}`
  }

  function getPersonName(item) {
    if (!item) return '-'
    const p = item.persona || item.persona_obj || item.person
    if (p && typeof p === 'object') {
      const parts = [p.nombres || p.nombre || p.first_name, p.apellido_paterno, p.apellido_materno].filter(Boolean)
      if (parts.length) return parts.join(' ').trim()
    }
    const flat = item.persona_nombre || item.person_name || item.nombre || item.name
    if (flat && String(flat).trim() !== '') return String(flat).trim()
    const id = item.persona_id || item.person_id || item.person || item.id_persona
    if (id) return String(id)
    return '-'
  }

  function getInstitutionName(item) {
    if (!item) return '-'
    // prefer resolved name fields
    const direct = item.institucion_nombre || item.institucion_name || item.sacrament_location || item.institucion || item.institucion_nombre
    // if direct is an object, try to extract .nombre
    if (direct && typeof direct === 'object') {
      const name = direct.nombre || direct.name || direct.institucion_nombre
      if (name && String(name).trim() !== '') return String(name).trim()
      // try id fallback
      const id = direct.id_institucion || direct.id
      return id != null ? String(id) : '-'
    }
    if (direct && String(direct).trim() !== '') return String(direct).trim()
    // last resort: fields on root
    if (item.nombre_institucion || item.name_institucion) return String(item.nombre_institucion || item.name_institucion)
    return '-'
  }

  // Client-side filtered list by persona name (simple substring match)
  const filteredSacramentos = sacramentos.filter((r) => {
    if (!searchTerm || String(searchTerm).trim() === '') return true
    const name = getPersonName(r)
    return String(name).toLowerCase().includes(String(searchTerm).toLowerCase())
  })

  // Helper to detect whether a sacramento is a matrimonio
  function isMatrimonio(item) {
    if (!item) return false
    const raw = item.tipo_id || item.tipo || item.tipo_nombre || item.tipo_sacramento
    if (raw == null) return false
    if (typeof raw === 'number' || /^\d+$/.test(String(raw))) return Number(raw) === 3
    return String(raw).toLowerCase().includes('matrim')
  }

  // Try many possible aliases to return the two spouse names for matrimonios
  function getSpouseNames(item) {
    if (!item) return ['-','-']
    const s1 = item.nombre_esposo || item.esposo || item.spouse_name || item.spouse || item.persona_nombre || item.person_name || (item.persona && typeof item.persona === 'string' ? item.persona : null) || item.nombre_conyuge || item.contrayente_1 || item.persona1 || null
    const s2 = item.nombre_esposa || item.esposa || item.spouse_name_2 || item.spouse2 || item.person2_name || item.contrayente_2 || item.persona2_nombre || item.persona2 || null

    const left = (s1 && String(s1).trim() !== '') ? s1 : null
    const right = (s2 && String(s2).trim() !== '') ? s2 : null

    if (!left && right) {
      const alt = item.persona_nombre || item.person_name || (item.persona && typeof item.persona === 'string' ? item.persona : null)
      return [alt || '-', right || '-']
    }
    if (!right && left) {
      const alt2 = item.nombre_conyuge || item.person2_name || item.persona2 || item.esposa || item.spouse2
      return [left || '-', alt2 || '-']
    }
    return [left || '-', right || '-']
  }

  function getParents(item) {
    if (!item) return '-'
    if (item.padres && String(item.padres).trim() !== '') return String(item.padres).trim()

    // Check combined stored field (personas.nombre_padre_nombre_madre)
    if (item.nombre_padre_nombre_madre && String(item.nombre_padre_nombre_madre).trim() !== '') return String(item.nombre_padre_nombre_madre).trim()

    // Check detalles_matrimonio / matrimonios nested object
    const mat = item.detalles_matrimonio || item.matrimonio || item.matrimonios
    if (mat && typeof mat === 'object') {
      const parts = []
      if (mat.nombre_padre_esposo || mat.nombre_madre_esposo) parts.push(`${mat.nombre_padre_esposo || '-'} y ${mat.nombre_madre_esposo || '-'}`)
      if (mat.nombre_padre_esposa || mat.nombre_madre_esposa) parts.push(`${mat.nombre_padre_esposa || '-'} y ${mat.nombre_madre_esposa || '-'}`)
      if (parts.length) return parts.join(' / ')
    }

    // Fallbacks on top-level and persona nested fields
    const padre = item.nombre_padre || (item.persona && (item.persona.nombre_padre || item.persona.padre)) || item.persona_padre || item.padre || item.father_name || ''
    const madre = item.nombre_madre || (item.persona && (item.persona.nombre_madre || item.persona.madre)) || item.persona_madre || item.madre || item.mother_name || ''
    if (padre || madre) return `${padre || '-'} y ${madre || '-'}`

    return '-'
  }

  function getPadrinos(item) {
    if (!item) return '-'

    // Direct fields on sacramento
    const raw = item.padrinos || item.nombre_padrino || item.nombre_padrinos || item.nombre_padrino_nombre_madrina || item.nombre_padrino_nombre_madrina
    if (raw && String(raw).trim() !== '') return String(raw).trim()

    // Check detalles_bautizo / detalles_confirmacion nested objects
    const db = item.detalles_bautizo || item.detalle_bautizo || item.detalles_bautizo_obj
    if (db && db.padrino && String(db.padrino).trim() !== '') return String(db.padrino).trim()
    const dc = item.detalles_confirmacion || item.detalle_confirmacion || item.detalles_confirmacion_obj
    if (dc && dc.padrino && String(dc.padrino).trim() !== '') return String(dc.padrino).trim()

    // Persona-level stored padrinos
    const p = item.persona || item.persona_obj
    if (p && typeof p === 'object') {
      const padr = p.nombre_padrino_nombre_madrina || p.nombre_padrino || p.nombre_padrinos
      if (padr && String(padr).trim() !== '') return String(padr).trim()
    }

    return '-'
  }

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
                  <div className="certificate-wrapper">
                    <div className="certificate">
                      <div className="cert-header">
                        <div className="cert-title">Certificado de {getTipoLabel(selected)}</div>
                        <div className="cert-sub">{getInstitutionName(selected) || 'Parroquia'}</div>
                      </div>
                      <div className="cert-body">
                        {isMatrimonio(selected) ? (() => {
                          const [esposoName, esposaName] = getSpouseNames(selected)
                          return (
                            <div>
                              <div className="field-label font-semibold">Contrayentes:</div>
                              <div className="contrayentes">
                                <div className="spouse">
                                  <div className="font-semibold">Esposo</div>
                                  <div>{esposoName}</div>
                                </div>
                                <div className="spouse">
                                  <div className="font-semibold">Esposa</div>
                                  <div>{esposaName}</div>
                                </div>
                              </div>
                            </div>
                          )
                        })() : (
                          <p><span className="field-label">Nombre:</span> {getPersonName(selected)}</p>
                        )}

                        <p><span className="field-label">Padres:</span> {getParents(selected)}</p>

                        <p><span className="field-label">Padrinos:</span> {getPadrinos(selected)}</p>

                        <p><span className="field-label">Fecha:</span> {selected.fecha_sacramento?.substring(0,10) || selected.fecha || selected.fecha_registro?.substring(0,10) || '-'}</p>

                        <p className="book-line"><span className="field-label">Libro:</span> {selected.libro_nombre || selected.libro || selected.libro_acta || (selected.libro_id ? `Libro ${selected.libro_id}` : '-')}</p>

                        <div className="footer">
                          <div className="issuer">
                            <div>Emitido por: Admin</div>
                            <div>Fecha: {new Date().toISOString().substring(0,10)}</div>
                          </div>
                          <div className="seal">
                            <div style={{height:56,width:56,borderRadius:28,background:'#eef6ff',display:'flex',alignItems:'center',justifyContent:'center',margin:'0 auto'}}>
                              <span className="material-symbols-outlined" style={{color:'#0b74ff'}}>workspace_premium</span>
                            </div>
                            <div style={{fontSize:12,marginTop:6,color:'#6b7280'}}>Sello Parroquial</div>
                          </div>
                        </div>
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
                        <td className="px-6 py-3">{getPersonName(r)}</td>
                        <td className="px-6 py-3">{getTipoLabel(r)}</td>
                        <td className="px-6 py-3">{r.fecha_sacramento?.substring(0,10) || r.fecha}</td>
                        <td className="px-6 py-3">
                          <button onClick={async () => {
                            const id = r.id_sacramento || r.id
                            try {
                              const resp = await fetch(`/api/v1/certificados/${id}`)
                              if (resp.ok) setSelected(await resp.json())
                              else setSelected(r)
                            } catch (e) { setSelected(r) }
                          }} className="px-3 py-1 rounded border border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark mr-2">Ver</button>
                          <button onClick={async () => {
                            const id = r.id_sacramento || r.id
                            try {
                              const resp = await fetch(`/api/v1/certificados/${id}`)
                              if (resp.ok) setSelected(await resp.json())
                              else setSelected(r)
                            } catch (e) { setSelected(r) }
                            // slight delay to allow preview render
                            setTimeout(() => handlePrint('certificate-preview'), 200)
                          }} className="px-3 py-1 rounded bg-primary text-white hover:bg-primary/90">Reimprimir</button>
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
