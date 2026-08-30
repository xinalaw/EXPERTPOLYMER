const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
export function buildUrl(path) {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return API_BASE ? `${API_BASE}${normalized}` : normalized
}

export function staticUrl(path) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  return buildUrl(path)
}

export async function parseApiError(response) {
  try {
    const data = await response.json()
    const { detail } = data

    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg || item.message || String(item)).join(', ')
    }

    return data.message || 'Ошибка запроса'
  } catch {
    return 'Ошибка запроса'
  }
}

export async function apiFetch(path, options = {}) {
  const { token, headers: customHeaders, ...rest } = options
  const headers = new Headers(customHeaders || {})

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  if (rest.body && !(rest.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(buildUrl(path), {
    ...rest,
    headers,
  })

  if (!response.ok) {
    const message = await parseApiError(response)
    throw new Error(message)
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}
