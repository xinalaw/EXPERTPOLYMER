import { computed, reactive, readonly } from 'vue'
import {
  clearStoredSession,
  getCurrentUser,
  getStoredSession,
  loginUser,
  storeSession,
} from '@/api/auth'
import type { StorageName } from '@/api/auth'
import { ApiError, onUnauthorized, setAuthToken } from '@/api/client'
import type { User } from '@/api/types'

const state = reactive({ user: null as User | null, ready: false, error: '', expired: false })
let activeSession: { token: string; storage: StorageName | null } | null = null
let restorePromise: Promise<void> | null = null
let restoreToken = ''
let generation = 0
let signingIn: number | null = null

function clearSession(expired = false, clearStorage = true) {
  generation++
  signingIn = null
  restorePromise = null
  activeSession = null
  setAuthToken(null)
  state.user = null
  state.error = ''
  state.expired = expired
  state.ready = true
  if (clearStorage) clearStoredSession()
}
onUnauthorized(() => clearSession(true))

export const auth = readonly(state)
export const isAuthenticated = computed(() => !!state.user)

export async function restoreSession(force = false) {
  if (signingIn !== null) return
  if (state.ready && !force) return
  const stored = getStoredSession()
  // A memory-only session survives storage failures; a removed persisted session does not.
  if (stored === null && activeSession?.storage != null) {
    clearSession(true, false)
    return
  }
  const candidate = stored || activeSession
  if (!candidate) {
    if (restorePromise) clearSession(true, false)
    else state.ready = true
    return
  }
  if (restorePromise && restoreToken === candidate.token) return restorePromise
  const requestGeneration = ++generation
  const alreadyVerified = activeSession?.token === candidate.token && !!state.user
  if (!alreadyVerified) {
    activeSession = null
    setAuthToken(null)
    state.user = null
    state.ready = false
  }
  state.error = ''
  restoreToken = candidate.token
  restorePromise = (async () => {
    try {
      const user = await getCurrentUser(candidate.token)
      if (generation !== requestGeneration) return
      activeSession = { token: candidate.token, storage: candidate.storage }
      setAuthToken(candidate.token)
      state.user = user
      state.expired = false
    } catch (error) {
      if (generation !== requestGeneration) return
      if (error instanceof ApiError && error.status === 401) clearSession(true)
      else state.error = error instanceof Error ? error.message : 'Не удалось восстановить сессию'
    } finally {
      if (generation === requestGeneration) {
        state.ready = true
        restorePromise = null
      }
    }
  })()
  return restorePromise
}

export async function signIn(email: string, password: string, remember: boolean) {
  const requestGeneration = ++generation
  signingIn = requestGeneration
  restorePromise = null
  try {
    const { user, token } = await loginUser(email, password)
    if (generation !== requestGeneration) throw new DOMException('Вход отменён', 'AbortError')
    activeSession = { token, storage: storeSession(user, token, remember) }
    setAuthToken(token)
    state.user = user
    state.error = ''
    state.expired = false
    state.ready = true
  } finally {
    if (signingIn === requestGeneration) {
      signingIn = null
      state.ready = true
    }
  }
}

export async function signOut() {
  clearSession()
}
