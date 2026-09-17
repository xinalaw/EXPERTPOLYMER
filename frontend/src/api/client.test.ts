import { afterEach, describe, expect, it, vi } from 'vitest'
import { apiFetch, ApiError, onUnauthorized, setAuthToken, staticUrl } from './client'

afterEach(() => {
  onUnauthorized(() => {})
  setAuthToken(null)
})
describe('API client', () => {
  it('sends the Bearer token and request header without inventing multipart content type', async () => {
    const fetch = vi.fn().mockImplementation(() => Promise.resolve(new Response('{"id":1}')))
    vi.stubGlobal('fetch', fetch)
    const body = new FormData()
    await apiFetch('/api/analyze', { method: 'POST', body })
    const options = fetch.mock.calls[0]![1]
    setAuthToken('secret-token')
    await apiFetch('/api/analyze', { method: 'POST', body })
    const authenticatedOptions = fetch.mock.calls[1]![1]
    expect(authenticatedOptions.headers.get('Authorization')).toBe('Bearer secret-token')
    expect(options.headers.get('X-Requested-With')).toBe('ExpertPolymer')
    expect(options.headers.has('Content-Type')).toBe(false)
  })
  it('preserves HTTP status and expires only authenticated requests on 401', async () => {
    setAuthToken('current-token')
    const expire = vi.fn()
    onUnauthorized(expire)
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockImplementation(() =>
          Promise.resolve(new Response('{"detail":"Сессия истекла"}', { status: 401 })),
        ),
    )
    await expect(apiFetch('/api/history')).rejects.toMatchObject({
      status: 401,
      message: 'Сессия истекла',
    })
    await expect(apiFetch('/api/auth/login', { notifyUnauthorized: false })).rejects.toBeInstanceOf(
      ApiError,
    )
    expect(expire).toHaveBeenCalledTimes(1)
  })
  it('does not expire a newer session when an older request returns 401', async () => {
    const expire = vi.fn()
    onUnauthorized(expire)
    let respond!: (response: Response) => void
    vi.stubGlobal(
      'fetch',
      vi.fn(
        () =>
          new Promise<Response>((resolve) => {
            respond = resolve
          }),
      ),
    )
    setAuthToken('old-token')
    const request = apiFetch('/api/history')
    setAuthToken('new-token')
    respond(new Response('{"detail":"Expired"}', { status: 401 }))
    await expect(request).rejects.toMatchObject({ status: 401 })
    expect(expire).not.toHaveBeenCalled()
  })
  it('does not expire an active session for an explicitly anonymous request', async () => {
    const expire = vi.fn()
    onUnauthorized(expire)
    setAuthToken('current-token')
    const fetch = vi.fn().mockResolvedValue(new Response('{}', { status: 401 }))
    vi.stubGlobal('fetch', fetch)
    await expect(apiFetch('/api/auth/login', { token: null })).rejects.toMatchObject({
      status: 401,
    })
    expect(fetch.mock.calls[0]![1].headers.has('Authorization')).toBe(false)
    expect(expire).not.toHaveBeenCalled()
  })
  it('supports an empty 204 response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })))
    await expect(apiFetch('/api/logout', { method: 'DELETE' })).resolves.toBeUndefined()
  })
  it('reports invalid JSON responses without exposing HTML', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>Vite fallback</html>')))
    await expect(apiFetch('/api/history')).rejects.toThrow('некорректный ответ')
  })
  it('times out a stalled request and releases the timer', async () => {
    vi.useFakeTimers()
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (_url, options) =>
          new Promise((_resolve, reject) => {
            options.signal.addEventListener('abort', () =>
              reject(new DOMException('Aborted', 'AbortError')),
            )
          }),
      ),
    )
    const request = expect(apiFetch('/api/analyze', { timeoutMs: 100 })).rejects.toThrow(
      'не ответил вовремя',
    )
    await vi.advanceTimersByTimeAsync(101)
    await request
    expect(vi.getTimerCount()).toBe(0)
  })
  it('distinguishes explicit cancellation from network failure', async () => {
    const controller = new AbortController()
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (_url, options) =>
          new Promise((_resolve, reject) => {
            options.signal.addEventListener('abort', () =>
              reject(new DOMException('Aborted', 'AbortError')),
            )
          }),
      ),
    )
    const request = apiFetch('/api/history', { signal: controller.signal })
    controller.abort()
    await expect(request).rejects.toMatchObject({ name: 'AbortError' })
  })
  it('rejects external, script and non-static image URLs', () => {
    expect(staticUrl('javascript:alert(1)')).toBe('')
    expect(staticUrl('https://untrusted.example/static/image.png')).toBe('')
    expect(staticUrl('/api/auth/me')).toBe('')
    expect(staticUrl('/static/uploads/a.png')).toContain('/static/uploads/a.png')
  })
})
