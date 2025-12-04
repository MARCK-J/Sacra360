import { useState } from 'react'
import Layout from '../components/Layout'
import PARROQUIAS from '../data/parroquias'

export default function Sacramento() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [form, setForm] = useState({
    tipo_sacramento: 1,
    fecha_sacramento: '',
    sacrament_location: '',
    sacrament_minister: '',
    person_name: '',
    person_birthdate: '',
    father_name: '',
    mother_name: '',
    // Campos para Matrimonio (segundo contrayente)
    spouse_name: '',
    spouse_birthdate: '',
    father2_name: '',
    mother2_name: '',
    persona2_id: '',
    godparent_1_name: '',
    book_number: '',
    folio_number: '',
    record_number: '',
    notes: ''
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    // tipo_sacramento must be a number so backend treats it as id, not as a name
    if (name === 'tipo_sacramento') {
      setForm((s) => ({ ...s, [name]: Number(value) }))
      return
    }
    setForm((s) => ({ ...s, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)
    try {
      // Client-side validations to avoid 422 from backend
      const nameTrim = (form.person_name || '').trim()
      if (!form.fecha_sacramento) {
        setMessage({ type: 'error', text: 'La fecha del sacramento es obligatoria.' })
        setLoading(false)
        return
      }
      if (!nameTrim && !form.persona_id) {
        setMessage({ type: 'error', text: 'Debe indicar la persona (nombre) o seleccionar una persona existente.' })
        setLoading(false)
        return
      }
        // Validaciones específicas para Matrimonio
        if (Number(form.tipo_sacramento) === 3) {
          const spouseTrim = (form.spouse_name || '').trim()
          const hasPersona2 = !!form.persona2_id
          if (!spouseTrim && !hasPersona2) {
            setMessage({ type: 'error', text: 'Matrimonio requiere indicar el segundo contrayente (nombre) o seleccionar persona existente.' })
            setLoading(false)
            return
          }
          const father2Trim = (form.father2_name || '').trim()
          const mother2Trim = (form.mother2_name || '').trim()
          if (!father2Trim || !mother2Trim) {
            setMessage({ type: 'error', text: 'Matrimonio requiere nombres de padre y madre del segundo contrayente.' })
            setLoading(false)
            return
          }
        }
      const tipoLabels = {1: 'bautizo', 2: 'confirmacion', 3: 'matrimonio', 4: 'defuncion'}
      const payload = {
        tipo_sacramento: Number(form.tipo_sacramento),
        tipo: tipoLabels[Number(form.tipo_sacramento)] || undefined,
        fecha_sacramento: form.fecha_sacramento,
        institucion: form.sacrament_location,
        ministro: form.sacrament_minister,
        person_name: form.person_name,
        person_birthdate: form.person_birthdate,
        father_name: form.father_name,
        mother_name: form.mother_name,
        // Enviar campos del segundo contrayente si existen (nombres compatibles con backend)
        spouse_name: form.spouse_name || undefined,
        spouse_birthdate: form.spouse_birthdate || undefined,
        father2_name: form.father2_name || undefined,
        mother2_name: form.mother2_name || undefined,
        persona2_id: form.persona2_id || undefined,
        godparent_1_name: form.godparent_1_name,
        libro: form.book_number,
        folio: form.folio_number,
        numero_acta: form.record_number,
        observaciones: form.notes
      }

      const res = await fetch('/api/v1/sacramentos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      // backend may return an empty body on success; parse safely
      const text = await res.text()
      let data = null
      try {
        data = text ? JSON.parse(text) : null
      } catch (err) {
        data = null
      }
      if (!res.ok) {
          // backend can return structured detail (array of field errors)
          let detail = text || res.statusText
          if (data?.detail) {
            if (Array.isArray(data.detail)) {
              detail = data.detail.map(d => d.message || JSON.stringify(d)).join('; ')
            } else if (typeof data.detail === 'string') {
              detail = data.detail
            } else {
              detail = JSON.stringify(data.detail)
            }
          }
          throw new Error(`${res.status} ${detail}`)
      }
      setMessage({ type: 'success', text: 'Sacramento creado (id: ' + (data?.id_sacramento || data?.id || 'ok') + ')' })
      // reset form or keep
    } catch (err) {
      setMessage({ type: 'error', text: String(err) })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout title="Registrar Nuevo Sacramento">
      <main className="p-8">
        <div className="max-w-6xl mx-auto flex flex-col gap-6">
          <div className="flex flex-wrap justify-between gap-3 items-center">
            <p className="text-gray-900 dark:text-white text-3xl font-bold leading-tight tracking-[-0.03em] min-w-72">Registrar Nuevo Sacramento</p>
          </div>

          <div className="flex">
            <div className="flex h-12 flex-1 items-center justify-center rounded-xl bg-gray-200 dark:bg-gray-800 p-1.5">
              {[{id:1,label:'Bautizo'},{id:2,label:'Confirmación'},{id:3,label:'Matrimonio'},{id:4,label:'Defunción'}].map((it)=>{
                const active = form.tipo_sacramento === it.id
                const base = 'flex cursor-pointer h-full grow items-center justify-center overflow-hidden rounded-lg px-4 text-sm font-medium leading-normal transition-all duration-200 select-none'
                const activeCls = active ? 'bg-white dark:bg-gray-900/80 text-primary shadow-md scale-105' : 'text-gray-500 dark:text-gray-400 hover:bg-white/50 dark:hover:bg-gray-700/50'
                return (
                  <button type="button" key={it.id} onClick={() => setForm(s=>({...s,tipo_sacramento: it.id}))} className={base + ' ' + activeCls}>
                    <span className="truncate">{it.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 rounded-xl p-8 flex flex-col gap-8">
            <div className="flex flex-col gap-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-800 pb-3">Datos del Sacramento</h3>
              <div className="grid grid-cols-1 gap-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="book-number">Libro N°</label>
                    <input name="book_number" value={form.book_number} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="book-number" placeholder="Ej: 10" type="text" />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="folio-number">Folio N°</label>
                    <input name="folio_number" value={form.folio_number} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="folio-number" placeholder="Ej: 45" type="text" />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="record-number">Partida N°</label>
                    <input name="record_number" value={form.record_number} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="record-number" placeholder="Ej: 200" type="text" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="sacrament-date">Fecha del Sacramento</label>
                    <input name="fecha_sacramento" value={form.fecha_sacramento} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="sacrament-date" type="date" />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="inst-select">Parroquia/Institución *</label>
                    <select id="inst-select" name="sacrament_location" value={form.sacrament_location} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                      <option value="">Seleccione una parroquia</option>
                      {PARROQUIAS.map((name, idx) => (
                        <option key={idx} value={name}>{name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="sacrament-minister">Ministro</label>
                    <input name="sacrament_minister" value={form.sacrament_minister} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="sacrament-minister" placeholder="Ej: P. Juan Pérez" type="text" />
                  </div>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-800 pb-3">
                {form.tipo_sacramento === 1 ? 'Datos del Bautizado' : form.tipo_sacramento === 2 ? 'Datos del Confirmando' : form.tipo_sacramento === 3 ? 'Datos de los Contrayentes' : 'Datos del Fallecido'}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="person-name">Nombres y Apellidos</label>
                  <input name="person_name" value={form.person_name} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="person-name" placeholder="Ingrese el nombre completo" type="text" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="person-birthdate">Fecha de Nacimiento</label>
                  <input name="person_birthdate" value={form.person_birthdate} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="person-birthdate" type="date" />
                </div>
              </div>
              {/* Sección para segundo contrayente en Matrimonio */}
              {form.tipo_sacramento === 3 && (
                <div className="mt-4 bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg border border-gray-100 dark:border-gray-800">
                  <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-3">Datos del Segundo Contrayente</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="spouse-name">Nombres y Apellidos (Contrayente 2)</label>
                      <input name="spouse_name" value={form.spouse_name} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="spouse-name" placeholder="Ingrese el nombre completo" type="text" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="spouse-birthdate">Fecha de Nacimiento (Contrayente 2)</label>
                      <input name="spouse_birthdate" value={form.spouse_birthdate} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="spouse-birthdate" type="date" />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="father2-name">Padre (Contrayente 2)</label>
                      <input name="father2_name" value={form.father2_name} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="father2-name" placeholder="Nombre completo del padre" type="text" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="mother2-name">Madre (Contrayente 2)</label>
                      <input name="mother2_name" value={form.mother2_name} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="mother2-name" placeholder="Nombre completo de la madre" type="text" />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex flex-col gap-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-800 pb-3">Familiares</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="father-name">Padre</label>
                  <input name="father_name" value={form.father_name} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="father-name" placeholder="Nombre completo del padre" type="text" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="mother-name">Madre</label>
                  <input name="mother_name" value={form.mother_name} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="mother-name" placeholder="Nombre completo de la madre" type="text" />
                </div>
              </div>
            </div>

            {form.tipo_sacramento === 1 && (
              <div className="flex flex-col gap-4">
                <div className="flex justify-between items-center border-b border-gray-200 dark:border-gray-800 pb-3">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">Padrinos</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="godparent-1-name">Padrino / Madrina 1</label>
                    <input name="godparent_1_name" value={form.godparent_1_name} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="godparent-1-name" placeholder="Nombre completo" type="text" />
                  </div>
                </div>
              </div>
            )}

            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="notes">Notas</label>
              <textarea name="notes" value={form.notes} onChange={handleChange} className="form-textarea rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="notes" placeholder="Añada cualquier observación o nota marginal." rows="3"></textarea>
            </div>

            <div className="flex justify-end gap-4 pt-4 border-t border-gray-200 dark:border-gray-800">
              <button type="button" className="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-11 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 gap-2 text-sm font-bold min-w-0 px-6 hover:bg-gray-300 dark:hover:bg-gray-600">
                Cancelar
              </button>
              <button type="submit" disabled={loading} className="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-11 bg-primary text-white gap-2 text-sm font-bold min-w-0 px-6 hover:bg-primary/90">
                {loading ? 'Guardando...' : 'Guardar Registro'}
              </button>
            </div>

            {message && (
              <div className={`mt-3 text-sm ${message.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>{message.text}</div>
            )}

          </form>
        </div>
      </main>
    </Layout>
  )
}
