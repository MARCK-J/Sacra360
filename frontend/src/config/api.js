const stripQuotes = (value) => {
  const v = String(value || '').trim()
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    return v.slice(1, -1).trim()
  }
  return v
}

const trimTrailingSlash = (value) => stripQuotes(value).replace(/\/+$/, '')

const normalizeToHttps = (value) => {
  const normalized = trimTrailingSlash(value)
  if (normalized.startsWith('http://')) {
    return `https://${normalized.slice('http://'.length)}`
  }
  if (normalized.startsWith('//')) {
    return `https:${normalized}`
  }
  return normalized
}

const defaultApiBase = 'http://localhost:8002'
const defaultAuthBase = 'http://localhost:8001'

const RAW_API_BASE_URL = trimTrailingSlash(
  import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || defaultApiBase
)

const RAW_AUTH_API_URL = trimTrailingSlash(
  import.meta.env.VITE_AUTH_API_URL || defaultAuthBase
)

export const API_BASE_URL = normalizeToHttps(RAW_API_BASE_URL)
export const AUTH_API_URL = normalizeToHttps(RAW_AUTH_API_URL)

export const API_V1_URL = `${API_BASE_URL}/api/v1`

export const apiV1Url = (path = '') => {
  if (!path) return API_V1_URL
  return path.startsWith('/') ? `${API_V1_URL}${path}` : `${API_V1_URL}/${path}`
}
