const trimTrailingSlash = (value) => String(value || '').replace(/\/+$/, '')

const defaultApiBase = 'http://localhost:8002'
const defaultAuthBase = 'http://localhost:8001'

export const API_BASE_URL = trimTrailingSlash(
  import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || defaultApiBase
)

export const AUTH_API_URL = trimTrailingSlash(
  import.meta.env.VITE_AUTH_API_URL || defaultAuthBase
)

export const API_V1_URL = `${API_BASE_URL}/api/v1`

export const apiV1Url = (path = '') => {
  if (!path) return API_V1_URL
  return path.startsWith('/') ? `${API_V1_URL}${path}` : `${API_V1_URL}/${path}`
}
