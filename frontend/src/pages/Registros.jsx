import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'

function getPersonaLabel(s) {
	if (!s) return '—'
	return s.persona_nombre || s.nombre || (s.persona && s.persona.nombre) || s.titular || s.contrayente || '—'
}

function getSacramentoType(s) {
	// Backend usually returns `tipo_nombre` (string). If not, try other fallbacks.
	const tipoNombre = s && (s.tipo_nombre || s.tipo_sacramento_nombre || s.tipo_sacramento || s.tipo)
	if (!tipoNombre && tipoNombre !== 0) return '—'
	// If it's already a string name, return it.
	if (typeof tipoNombre === 'string' && isNaN(Number(tipoNombre))) return tipoNombre
	// If it's numeric (id), map common ids to names as fallback.
	const id = Number(tipoNombre)
	const map = {1: 'bautizo', 2: 'confirmacion', 3: 'matrimonio', 4: 'defuncion', 5: 'primera comunion'}
	return map[id] || String(tipoNombre)
}

function getYear(s) {
	const candidates = [s && s.fecha, s && s.fecha_sacramento, s && s.fecha_defuncion, s && s.fecha_nacimiento]
	for (const c of candidates) {
		if (!c) continue
		try {
			const y = String(c).slice(0, 4)
			if (/^\d{4}$/.test(y)) return y
		} catch (e) {}
	}
	return '—'
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8002'

export default function Registros() {
	const [items, setItems] = useState([])
	const [loading, setLoading] = useState(false)
	const [viewItem, setViewItem] = useState(null)
	const [editItem, setEditItem] = useState(null)
	const [editForm, setEditForm] = useState(null)
	const [confirmDelete, setConfirmDelete] = useState(null)

	// Filters
	const [filterYear, setFilterYear] = useState('')
	const [filterParish, setFilterParish] = useState('')
	const [searchTerm, setSearchTerm] = useState('')
	useEffect(() => {
		load()
	}, [])

	// derived filter options
	const years = Array.from(new Set(items.map((it) => getYear(it)).filter((y) => y && y !== '—'))).sort()
	const parishes = Array.from(new Set(items.map((it) => (it.institucion_nombre || it.institucion || '').trim()).filter((p) => p))).sort()

	const filteredItems = items.filter((it) => {
		if (filterYear && getYear(it) !== filterYear) return false
		if (filterParish && ((it.institucion_nombre || it.institucion || '').trim() !== filterParish)) return false
		if (searchTerm && !getPersonaLabel(it).toLowerCase().includes(searchTerm.toLowerCase())) return false
		return true
	})

	async function load() {
		setLoading(true)
		try {
			const res = await fetch(`${API_BASE}/api/v1/sacramentos?limit=100`)
			if (!res.ok) throw new Error(await res.text())
			const data = await res.json()
			setItems(Array.isArray(data) ? data : data.items || [])
		} catch (err) {
			console.error(err)
			alert('Error cargando registros: ' + (err.message || err))
		} finally {
			setLoading(false)
		}
	}

	function estadoBadge(s) {
		// Backend doesn't have an `estado` column; fallbacks: explicit estado fields or markers in `observaciones`.
		const e = (s && (s.estado || s.estado_ui || s.estado_local)) || ''
		const obs = (s && (s.observaciones || s.observacion || s.notes || '')) || ''
		// If observaciones contains 'complet' mark as completed
		if (String(e).toLowerCase() === 'completado' || /complet/i.test(obs)) {
			return <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completado</span>
		}
		if (String(e).toLowerCase() === 'pendiente' || !e) {
			return <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">Pendiente</span>
		}
		return <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">{String(e)}</span>
	}

	async function handleAcceptWithoutChanges(item) {
		try {
			const id = item.id_sacramento || item.id || item.id_sacrament
			// Backend only allows specific fields for update. Use `observaciones` to mark completion.
			const existingObs = item.observaciones || item.observacion || ''
			const newObs = existingObs ? `${existingObs} | estado:completado` : 'estado:completado'
			const res = await fetch(`${API_BASE}/api/v1/sacramentos/${id}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ observaciones: newObs })
			})
			if (!res.ok) throw new Error(await res.text())
			alert('Registro aceptado')
			load()
			setEditItem(null)
		} catch (err) {
			console.error(err)
			alert('Error al aceptar: ' + (err.message || err))
		}
	}

	function openEdit(item) {
		// Prepare a small textual form (only text fields that we can safely update)
		setEditItem(item)
		setEditForm({
			fecha_sacramento: item.fecha_sacramento || '',
			libro_id: item.libro_id || '',
			observaciones: item.observaciones || item.observacion || '',
			ministro: item.ministro || item.sacrament_minister || item.ministro_confirmacion || item.ministro_bautizo || '',
			folio: item.foja || item.folio || '',
			numero_acta: item.numero_acta || item.numero || '' ,
			pagina: item.pagina || ''
		})
	}

	async function handleSaveAndAccept() {
		if (!editItem || !editForm) return
		// Build payload from editForm allowing only permitted keys
		const allowed = new Set(['persona_id', 'tipo_id', 'usuario_id', 'institucion_id', 'libro_id', 'fecha_sacramento', 'ministro', 'padrinos', 'observaciones', 'folio', 'numero_acta', 'pagina'])
		const payload = {}
		if (editForm.fecha_sacramento) payload.fecha_sacramento = editForm.fecha_sacramento
		if (editForm.libro_id) payload.libro_id = Number(editForm.libro_id)
		if (typeof editForm.observaciones === 'string') payload.observaciones = editForm.observaciones
		if (typeof editForm.ministro === 'string' && editForm.ministro.trim() !== '') payload.ministro = editForm.ministro
		if (editForm.folio) payload.folio = editForm.folio
		if (editForm.numero_acta) payload.numero_acta = editForm.numero_acta
		if (editForm.pagina) payload.pagina = editForm.pagina
		// mark completed in observaciones
		const existingObs = editItem.observaciones || editItem.observacion || ''
		payload.observaciones = existingObs ? `${existingObs} | estado:completado` : (payload.observaciones ? `${payload.observaciones} | estado:completado` : 'estado:completado')

		try {
			const id = editItem.id_sacramento || editItem.id || editItem.id_sacrament
			const res = await fetch(`${API_BASE}/api/v1/sacramentos/${id}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			})
			if (!res.ok) throw new Error(await res.text())
			alert('Registro guardado y aceptado')
			setEditItem(null)
			setEditForm(null)
			load()
		} catch (err) {
			console.error(err)
			alert('Error al guardar: ' + (err.message || err))
		}
	}

	async function handleDeleteConfirmed() {
		if (!confirmDelete) return
		try {
			const id = confirmDelete.id_sacramento || confirmDelete.id || confirmDelete.id_sacrament
			const res = await fetch(`${API_BASE}/api/v1/sacramentos/${id}`, { method: 'DELETE' })
			if (!res.ok) throw new Error(await res.text())
			alert('Registro eliminado')
			setConfirmDelete(null)
			load()
		} catch (err) {
			console.error(err)
			alert('Error al eliminar: ' + (err.message || err))
		}
	}

	return (
		<Layout title="Gestión de Registros">
			<div className="bg-white dark:bg-gray-900/50 rounded-lg shadow">
				<div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-800">
					<div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
						<div className="flex items-center gap-3 w-full">
							<div className="relative w-full sm:w-72">
								<span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">search</span>
								<input value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary" placeholder="Buscar por persona..." type="text" />
							</div>
							<select value={filterYear} onChange={(e) => setFilterYear(e.target.value)} className="form-select border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg">
								<option value="">Año</option>
								{years.map((y) => <option key={y} value={y}>{y}</option>)}
							</select>
							<select value={filterParish} onChange={(e) => setFilterParish(e.target.value)} className="form-select border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg">
								<option value="">Parroquia</option>
								{parishes.map((p) => <option key={p} value={p}>{p}</option>)}
							</select>
						</div>
						<div>
							<button onClick={() => { setFilterYear(''); setFilterParish(''); setSearchTerm(''); load(); }} className="btn">{loading ? 'Cargando...' : 'Refrescar'}</button>
						</div>
					</div>
				</div>

				<div className="overflow-x-auto">
					<table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
						<thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-800">
							<tr>
								<th className="px-6 py-3">Persona</th>
								<th className="px-6 py-3">Sacramento</th>
								<th className="px-6 py-3">Año</th>
								<th className="px-6 py-3">Estado</th>
								<th className="px-6 py-3 text-center">Acciones</th>
							</tr>
						</thead>
						<tbody>
							{filteredItems.map((it) => (
								<tr key={it.id_sacramento || it.id || it.id_sacrament} className="bg-white dark:bg-gray-900/50 border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
									<th className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">{getPersonaLabel(it)}</th>
									<td className="px-6 py-4">{getSacramentoType(it)}</td>
									<td className="px-6 py-4">{getYear(it)}</td>
									<td className="px-6 py-4">{estadoBadge(it)}</td>
									<td className="px-6 py-4 text-center space-x-2">
										<button title="Ver" onClick={() => setViewItem(it)} className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">visibility</span></button>
										<button title="Editar" onClick={() => openEdit(it)} className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">edit</span></button>
										<button title="Aceptar sin cambios" onClick={() => { if (confirm('Aceptar sin cambios y marcar como completado?')) handleAcceptWithoutChanges(it) }} className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">check_circle</span></button>
										<button title="Eliminar" onClick={() => setConfirmDelete(it)} className="p-1 rounded-full text-red-500 hover:bg-red-100 dark:hover:bg-red-900/20"><span className="material-symbols-outlined text-base">delete</span></button>
									</td>
								</tr>
							))}
							{filteredItems.length === 0 && !loading && (
								<tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No hay registros</td></tr>
							)}
						</tbody>
					</table>
				</div>

				<div className="p-4 border-t border-gray-200 dark:border-gray-800 flex items-center justify-between">
					<span className="text-sm text-gray-700 dark:text-gray-400">Mostrando {filteredItems.length} registros</span>
				</div>
			</div>

			{/* View modal */}
			{viewItem && (
				<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
					<div className="bg-white dark:bg-gray-900 w-[90%] max-w-3xl rounded-lg p-4">
						<div className="flex items-center justify-between mb-2">
							<h3 className="text-lg font-medium">Ver Registro</h3>
							<button onClick={() => setViewItem(null)} className="text-gray-500">Cerrar</button>
						</div>
						<div className="max-h-[60vh] overflow-auto text-sm bg-gray-50 dark:bg-gray-800 p-4 rounded">
							<div className="mb-3"><strong>Persona:</strong> {getPersonaLabel(viewItem)}</div>
							<div className="mb-3"><strong>Sacramento:</strong> {getSacramentoType(viewItem)}</div>
							<div className="mb-3"><strong>Fecha del sacramento:</strong> {viewItem.fecha_sacramento || '—'}</div>
							<div className="mb-3"><strong>Ministro:</strong> {viewItem.ministro || viewItem.sacrament_minister || viewItem.ministro_confirmacion || viewItem.ministro_bautizo || '—'}</div>
							<div className="mb-3"><strong>Parroquia / Institución:</strong> {viewItem.institucion_nombre || viewItem.institucion || '—'}</div>
							<div className="mb-3"><strong>Libro:</strong> {viewItem.libro_nombre || viewItem.libro_id || '—'}</div>
							<div className="mb-3"><strong>Foja / Folio:</strong> {viewItem.foja || viewItem.folio || '—'}</div>
							<div className="mb-3"><strong>Número acta:</strong> {viewItem.numero_acta || viewItem.numero || '—'}</div>
							<div className="mb-3"><strong>Página:</strong> {viewItem.pagina || '—'}</div>
							<div className="mb-3"><strong>Observaciones:</strong> {viewItem.observaciones || viewItem.observacion || '—'}</div>
							{/* show detail textual fields if present */}
							{viewItem.nombre_esposo && <div className="mb-2"><strong>Esposo:</strong> {viewItem.nombre_esposo}</div>}
							{viewItem.nombre_esposa && <div className="mb-2"><strong>Esposa:</strong> {viewItem.nombre_esposa}</div>}
							{viewItem.persona_padre && <div className="mb-2"><strong>Padre:</strong> {viewItem.persona_padre}</div>}
							{viewItem.persona_madre && <div className="mb-2"><strong>Madre:</strong> {viewItem.persona_madre}</div>}
						</div>
					</div>
				</div>
			)}

			{/* Edit modal */}
			{editItem && editForm && (
				<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
					<div className="bg-white dark:bg-gray-900 w-[95%] max-w-4xl rounded-lg p-4">
						<div className="flex items-center justify-between mb-2">
							<h3 className="text-lg font-medium">Editar Registro</h3>
							<button onClick={() => { setEditItem(null); setEditForm(null) }} className="text-gray-500">Cerrar</button>
						</div>
						<div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
							<div>
								<label className="block text-sm mb-1">Persona</label>
								<div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">{getPersonaLabel(editItem)}</div>
							</div>
							<div>
								<label className="block text-sm mb-1">Sacramento</label>
								<div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">{getSacramentoType(editItem)}</div>
							</div>
							<div>
								<label className="block text-sm mb-1">Fecha sacramento</label>
								<input type="date" value={editForm.fecha_sacramento || ''} onChange={(e) => setEditForm({...editForm, fecha_sacramento: e.target.value})} className="form-input w-full" />
							</div>
							<div>
								<label className="block text-sm mb-1">Libro (ID)</label>
								<input type="text" value={editForm.libro_id || ''} onChange={(e) => setEditForm({...editForm, libro_id: e.target.value})} className="form-input w-full" />
							</div>
							<div>
								<label className="block text-sm mb-1">Ministro</label>
								<input type="text" value={editForm.ministro || ''} onChange={(e) => setEditForm({...editForm, ministro: e.target.value})} className="form-input w-full" />
							</div>
							<div className="sm:col-span-2">
								<label className="block text-sm mb-1">Observaciones</label>
								<textarea rows={4} value={editForm.observaciones || ''} onChange={(e) => setEditForm({...editForm, observaciones: e.target.value})} className="w-full p-2 rounded border bg-gray-50 dark:bg-gray-800" />
							</div>
							<div>
								<label className="block text-sm mb-1">Foja / Folio</label>
								<input type="text" value={editForm.folio || ''} onChange={(e) => setEditForm({...editForm, folio: e.target.value})} className="form-input w-full" />
							</div>
							<div>
								<label className="block text-sm mb-1">Número acta</label>
								<input type="text" value={editForm.numero_acta || ''} onChange={(e) => setEditForm({...editForm, numero_acta: e.target.value})} className="form-input w-full" />
							</div>
							<div>
								<label className="block text-sm mb-1">Página</label>
								<input type="text" value={editForm.pagina || ''} onChange={(e) => setEditForm({...editForm, pagina: e.target.value})} className="form-input w-full" />
							</div>
						</div>
						<div className="flex gap-2 justify-end">
							<button onClick={() => { setEditItem(null); setEditForm(null) }} className="px-3 py-1 rounded bg-gray-200">Cancelar</button>
							<button onClick={() => handleAcceptWithoutChanges(editItem)} className="px-3 py-1 rounded bg-yellow-500 text-white">Aceptar sin cambios</button>
							<button onClick={handleSaveAndAccept} className="px-3 py-1 rounded bg-green-600 text-white">Guardar y Aceptar</button>
						</div>
					</div>
				</div>
			)}

			{/* Delete confirm modal */}
			{confirmDelete && (
				<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
					<div className="bg-white dark:bg-gray-900 w-full max-w-lg rounded-lg p-4">
						<h3 className="text-lg font-medium mb-2">Confirmar eliminación</h3>
						<p className="mb-4">¿Eliminar el registro de <strong>{getPersonaLabel(confirmDelete)}</strong>? Esta acción no se puede deshacer.</p>
						<div className="flex gap-2 justify-end">
							<button onClick={() => setConfirmDelete(null)} className="px-3 py-1 rounded bg-gray-200">Cancelar</button>
							<button onClick={handleDeleteConfirmed} className="px-3 py-1 rounded bg-red-600 text-white">Eliminar</button>
						</div>
					</div>
				</div>
			)}
		</Layout>
	)
}

