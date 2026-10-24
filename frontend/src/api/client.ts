const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(
    message: string,
    public status = 0,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

let unauthorizedHandler: () => void = () => {}
let authToken = ''
let authVersion = 0
export function setAuthToken(token?: string | null) {
  authVersion++
  authToken = token || ''
}
export function onUnauthorized(handler: () => void) {
  unauthorizedHandler = handler
}

export function buildUrl(path: string) {
  return `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`
}

export function staticUrl(path?: string | null) {
  if (!path) return ''
  // Result images must be served by our backend, never arbitrary external origins.
  const base = new URL(API_BASE || window.location.origin, window.location.origin)
  try {
    const url = new URL(path, base)
    return url.origin === base.origin && url.pathname.startsWith('/static/') ? url.href : ''
  } catch {
    return ''
  }
}

export async function parseApiError(response: Response): Promise<string> {
  const fallback =
    response.status >= 500
      ? 'Сервер временно недоступен. Попробуйте позже.'
      : 'Не удалось выполнить запрос.'
  try {
    const data = await response.json()
    if (typeof data.detail === 'string') return data.detail
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item: { msg?: string }) => item.msg || 'Проверьте введённые данные')
        .join('. ')
    }
    return typeof data.message === 'string' ? data.message : fallback
  } catch {
    return fallback
  }
}

interface ApiOptions extends RequestInit {
  timeoutMs?: number
  notifyUnauthorized?: boolean
  token?: string | null
}

export async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { timeoutMs = 30000, notifyUnauthorized = true, token, signal, ...rest } = options
  const requestToken = token === undefined ? authToken : token || ''
  const requestAuthVersion = authVersion
  const controller = new AbortController()
  let timedOut = false
  const cancel = () => controller.abort()
  if (signal?.aborted) cancel()
  signal?.addEventListener('abort', cancel, { once: true })
  const timer = setTimeout(() => {
    timedOut = true
    cancel()
  }, timeoutMs)
  const headers = new Headers(rest.headers)
  headers.set('X-Requested-With', 'GranulAI')
  if (requestToken) headers.set('Authorization', `Bearer ${requestToken}`)
  else headers.delete('Authorization')
  if (rest.body && !(rest.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  try {
    const response = await fetch(buildUrl(path), {
      ...rest,
      headers,
      signal: controller.signal,
    })
    if (!response.ok) {
      if (
        response.status === 401 &&
        notifyUnauthorized &&
        requestToken &&
        requestToken === authToken &&
        requestAuthVersion === authVersion
      )
        unauthorizedHandler()
      throw new ApiError(await parseApiError(response), response.status)
    }
    if (response.status === 204) return undefined as T
    try {
      return (await response.json()) as T
    } catch {
      throw new ApiError(
        'Сервер вернул некорректный ответ. Проверьте подключение к API.',
        response.status,
      )
    }
  } catch (error) {
    if (timedOut)
      throw new ApiError('Сервер не ответил вовремя. Проверьте историю перед повторным анализом.')
    if (controller.signal.aborted) throw new DOMException('Запрос отменён', 'AbortError')
    if (error instanceof ApiError) throw error
    throw new ApiError('Нет соединения с сервером. Проверьте подключение и повторите попытку.')
  } finally {
    clearTimeout(timer)
    signal?.removeEventListener('abort', cancel)
  }
}
