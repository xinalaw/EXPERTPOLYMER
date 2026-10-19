import { beforeEach, expect, it, vi } from 'vitest'
import { apiFetch } from '@/api/client'
import { SESSION_KEY, getStoredSession } from '@/api/auth'
import { auth, restoreSession, signIn, signOut } from './auth'

const user = { id: 1, username: 'Test User', email: 'test@example.com', role: 'researcher' }
const saved = JSON.stringify({ user, token: 'test-token' })
const fetchMock = vi.fn<typeof fetch>()
let profileStatus = 200

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), { status })
}
async function authorization() {
  await apiFetch('/probe')
  return new Headers(fetchMock.mock.lastCall?.[1]?.headers).get('Authorization')
}
beforeEach(async () => {
  await signOut()
  localStorage.clear()
  sessionStorage.clear()
  profileStatus = 200
  fetchMock.mockImplementation(async (url, options) => {
    if (url === '/api/auth/login') return json({ access_token: 'test-token', token_type: 'bearer' })
    if (url === '/api/auth/me') {
      expect(new Headers(options?.headers).get('Authorization')).toBe('Bearer test-token')
      return json(profileStatus === 200 ? user : { detail: 'Profile unavailable' }, profileStatus)
    }
    return json({})
  })
  vi.stubGlobal('fetch', fetchMock)
})

it.each([false, true])(
  'signs in and persists the chosen session (remember=%s)',
  async (remember) => {
    await signIn(user.email, 'test12345', remember)
    expect(auth.user).toEqual(user)
    expect(window[remember ? 'localStorage' : 'sessionStorage'].getItem(SESSION_KEY)).toBe(saved)
    expect(window[remember ? 'sessionStorage' : 'localStorage'].getItem(SESSION_KEY)).toBeNull()
    expect(await authorization()).toBe('Bearer test-token')
  },
)

it('does not activate a token if profile loading fails during login', async () => {
  profileStatus = 503
  await expect(signIn(user.email, 'test12345', true)).rejects.toMatchObject({ status: 503 })
  expect(auth.user).toBeNull()
  expect(getStoredSession()).toBeNull()
  expect(await authorization()).toBeNull()
})

it.each(['localStorage', 'sessionStorage'] as const)(
  'fully clears an expired session from %s',
  async (name) => {
    window[name].setItem(SESSION_KEY, saved)
    profileStatus = 401
    await restoreSession(true)
    expect(auth.user).toBeNull()
    expect(auth.expired).toBe(true)
    expect(auth.ready).toBe(true)
    expect(getStoredSession()).toBeNull()
    expect(await authorization()).toBeNull()
    const calls = fetchMock.mock.calls.length
    await restoreSession(true)
    expect(fetchMock).toHaveBeenCalledTimes(calls)
  },
)

it('notices a remembered session removed by another tab', async () => {
  await signIn(user.email, 'test12345', true)
  localStorage.removeItem(SESSION_KEY)
  await restoreSession(true)
  expect(auth.user).toBeNull()
  expect(await authorization()).toBeNull()
})

it('keeps an independent tab session when shared storage changes', async () => {
  await signIn(user.email, 'test12345', false)
  localStorage.removeItem(SESSION_KEY)
  await restoreSession(true)
  expect(auth.user).toEqual(user)
  expect(await authorization()).toBe('Bearer test-token')
})

it('keeps a verified session on a temporary server failure', async () => {
  await signIn(user.email, 'test12345', false)
  profileStatus = 503
  await restoreSession(true)
  expect(auth.user).toEqual(user)
  expect(auth.error).not.toBe('')
  expect(await authorization()).toBe('Bearer test-token')
})

it('does not authenticate an unverified cached profile when the server is unavailable', async () => {
  localStorage.setItem(SESSION_KEY, saved)
  profileStatus = 503
  await restoreSession(true)
  expect(auth.user).toBeNull()
  expect(auth.error).not.toBe('')
  expect(await authorization()).toBeNull()
  profileStatus = 200
  await restoreSession(true)
  expect(auth.user).toEqual(user)
})

it('supports login, focus refresh and logout with inaccessible storage', async () => {
  for (const name of ['localStorage', 'sessionStorage'] as const) {
    vi.spyOn(window, name, 'get').mockImplementation(() => {
      throw new DOMException('Blocked', 'SecurityError')
    })
  }
  await signIn(user.email, 'test12345', true)
  await restoreSession(true)
  expect(auth.user).toEqual(user)
  expect(await authorization()).toBe('Bearer test-token')
  await signOut()
  expect(auth.user).toBeNull()
  expect(await authorization()).toBeNull()
})

it('retains a memory session when storage is readable but its quota is exhausted', async () => {
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
    throw new DOMException('Full', 'QuotaExceededError')
  })
  await signIn(user.email, 'test12345', false)
  expect(getStoredSession()).toBeNull()
  await restoreSession(true)
  expect(auth.user).toEqual(user)
  expect(await authorization()).toBe('Bearer test-token')
})

it.each(['logout', 'storage removal'] as const)(
  'does not revive an in-flight restore after %s',
  async (action) => {
    localStorage.setItem(SESSION_KEY, saved)
    let respond!: (response: Response) => void
    fetchMock.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          respond = resolve
        }),
    )
    const restore = restoreSession(true)
    if (action === 'logout') await signOut()
    else {
      localStorage.removeItem(SESSION_KEY)
      await restoreSession(true)
    }
    respond(json(user))
    await restore
    expect(auth.user).toBeNull()
    expect(await authorization()).toBeNull()
  },
)

it('does not complete a pending login after logout', async () => {
  let respond!: (response: Response) => void
  fetchMock.mockImplementationOnce(
    () =>
      new Promise((resolve) => {
        respond = resolve
      }),
  )
  const login = signIn(user.email, 'test12345', true)
  await signOut()
  respond(json({ access_token: 'test-token', token_type: 'bearer' }))
  await expect(login).rejects.toMatchObject({ name: 'AbortError' })
  expect(auth.user).toBeNull()
  expect(getStoredSession()).toBeNull()
  expect(await authorization()).toBeNull()
})

it('clears the token and any connection error on logout', async () => {
  await signIn(user.email, 'test12345', false)
  profileStatus = 503
  await restoreSession(true)
  await signOut()
  expect(auth.user).toBeNull()
  expect(auth.error).toBe('')
  expect(getStoredSession()).toBeNull()
  expect(await authorization()).toBeNull()
})
