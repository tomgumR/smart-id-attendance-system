const BASE = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000/api`

export function token() { return localStorage.getItem('token') }
export async function api(path, options = {}) {
  const headers = new Headers(options.headers || {})
  if (token()) headers.set('Authorization', `Bearer ${token()}`)
  if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  const response = await fetch(`${BASE}${path}`, { ...options, headers })
  if (!response.ok) {
    let detail = 'Request failed'
    try { detail = (await response.json()).detail || detail } catch { /* no JSON body */ }
    throw new Error(Array.isArray(detail) ? detail.map(x => x.msg).join(', ') : detail)
  }
  if (response.status === 204) return null
  return response
}

export async function json(path, options) { return (await api(path, options)).json() }
