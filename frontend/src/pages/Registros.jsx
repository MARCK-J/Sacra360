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
	const [editRaw, setEditRaw] = useState('')
	const [confirmDelete, setConfirmDelete] = useState(null)

	useEffect(() => {
		load()
	}, [])

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
		setEditItem(item)
		setEditRaw(JSON.stringify(item, null, 2))
	}

	async function handleSaveAndAccept() {
		if (!editItem) return
		let parsed
		try {
			parsed = JSON.parse(editRaw)
		} catch (err) {
			alert('JSON inválido: ' + err.message)
			return
		}
		// Filter parsed to only allowed update keys on backend
		const allowed = new Set(['persona_id', 'tipo_id', 'usuario_id', 'institucion_id', 'libro_id', 'fecha_sacramento', 'ministro', 'padrinos', 'observaciones', 'folio', 'numero_acta', 'pagina'])
		const payload = {}
		for (const k of Object.keys(parsed)) {
			if (allowed.has(k)) payload[k] = parsed[k]
		}
		// ensure we mark completion via observaciones
		const existingObs = editItem.observaciones || editItem.observacion || ''
		payload.observaciones = existingObs ? `${existingObs} | estado:completado` : 'estado:completado'

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
				<div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
					<div className="flex items-center gap-4 w-full">
						<div className="relative w-full sm:w-72">
							<span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">search</span>
							<input className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary" placeholder="Buscar por persona, sacramento..." type="text" />
						</div>
					</div>
					<div>
						<button onClick={load} className="btn">{loading ? 'Cargando...' : 'Refrescar'}</button>
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
							{items.map((it) => (
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
							{items.length === 0 && !loading && (
								<tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No hay registros</td></tr>
							)}
						</tbody>
					</table>
				</div>

				<div className="p-4 border-t border-gray-200 dark:border-gray-800 flex items-center justify-between">
					<span className="text-sm text-gray-700 dark:text-gray-400">Mostrando {items.length} registros</span>
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
						<pre className="whitespace-pre-wrap max-h-[60vh] overflow-auto text-xs bg-gray-100 dark:bg-gray-800 p-3 rounded">{JSON.stringify(viewItem, null, 2)}</pre>
					</div>
				</div>
			)}

			{/* Edit modal */}
			{editItem && (
				<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
					<div className="bg-white dark:bg-gray-900 w-[95%] max-w-4xl rounded-lg p-4">
						<div className="flex items-center justify-between mb-2">
							<h3 className="text-lg font-medium">Editar Registro</h3>
							<button onClick={() => setEditItem(null)} className="text-gray-500">Cerrar</button>
						</div>
						<div className="mb-3">
							<label className="block text-sm mb-1">Editar JSON (raw)</label>
							<textarea value={editRaw} onChange={(e) => setEditRaw(e.target.value)} rows={12} className="w-full font-mono text-xs p-2 rounded border bg-gray-50 dark:bg-gray-800" />
						</div>
						<div className="flex gap-2 justify-end">
							<button onClick={() => setEditItem(null)} className="px-3 py-1 rounded bg-gray-200">Cancelar</button>
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

