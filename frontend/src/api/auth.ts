import { apiFetch, ApiError } from './client'
import type { User } from './types'

export const SESSION_KEY = 'expert-polymer-session'
export type StorageName = 'sessionStorage' | 'localStorage'
export interface StoredSession {
  user: User
  token: string
  storage: StorageName
}

export interface Registration {
  first_name: string
  last_name: string
  email: string
  organization?: string | null
  password: string
  password_confirm: string
}

export function registerUser(data: Registration) {
  return apiFetch<User>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
    notifyUnauthorized: false,
    token: null,
  })
}

export async function loginUser(email: string, password: string) {
  const tokenData = await apiFetch<{ access_token: string; token_type: string }>(
    '/api/auth/login',
    {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      notifyUnauthorized: false,
      token: null,
    },
  )
  if (typeof tokenData?.access_token !== 'string' || !tokenData.access_token.trim()) {
    throw new ApiError('Сервер не вернул токен доступа. Повторите вход.')
  }
  const user = await getCurrentUser(tokenData.access_token)
  return { user, token: tokenData.access_token }
}

function isUser(value: unknown): value is User {
  if (!value || typeof value !== 'object') return false
  const user = value as Partial<User>
  return (
    Number.isSafeInteger(user.id) &&
    Number(user.id) > 0 &&
    typeof user.username === 'string' &&
    typeof user.email === 'string' &&
    typeof user.role === 'string'
  )
}

export async function getCurrentUser(token?: string) {
  const user = await apiFetch<User>('/api/auth/me', { notifyUnauthorized: false, token })
  if (!isUser(user))
    throw new ApiError('Сервер вернул некорректные данные профиля. Повторите вход.')
  return user
}

// undefined means storage is unavailable, not that the user signed out elsewhere.
export function getStoredSession(): StoredSession | null | undefined {
  let unavailable = false
  for (const name of ['sessionStorage', 'localStorage'] as const) {
    try {
      const storage = window[name]
      const raw = storage.getItem(SESSION_KEY)
      if (!raw) continue
      try {
        const value = JSON.parse(raw)
        if (isUser(value?.user) && typeof value.token === 'string' && value.token.trim()) {
          return { user: value.user, token: value.token, storage: name }
        }
      } catch {
        /* Discard malformed saved sessions and try the other storage. */
      }
      storage.removeItem(SESSION_KEY)
    } catch {
      unavailable = true
    }
  }
  return unavailable ? undefined : null
}

export function storeSession(user: User, token: string, remember: boolean): StorageName | null {
  clearStoredSession()
  try {
    const name = remember ? 'localStorage' : 'sessionStorage'
    window[name].setItem(SESSION_KEY, JSON.stringify({ user, token }))
    return name
  } catch {
    return null /* The in-memory session remains usable. */
  }
}

export function clearStoredSession() {
  for (const name of ['localStorage', 'sessionStorage'] as const) {
    try {
      const storage = window[name]
      storage.removeItem(SESSION_KEY)
      storage.removeItem('user')
    } catch {
      /* Storage can be disabled. */
    }
  }
}
