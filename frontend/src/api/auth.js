import { apiFetch } from './client'

export function mapUserToStorage(user, token) {
  return {
    id: user.id,
    email: user.email,
    username: user.username,
    role: user.role,
    directorId: user.director_id ?? null,
    name: user.username,
    token,
  }
}

export function getStoredUser() {
  const raw = localStorage.getItem('user') || sessionStorage.getItem('user')
  if (!raw) return null

  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function getAuthToken() {
  return getStoredUser()?.token ?? null
}

export function registerUser(data) {
  return apiFetch('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      first_name: data.first_name,
      last_name: data.last_name,
      email: data.email,
      organization: data.organization || null,
      password: data.password,
      password_confirm: data.password_confirm,
    }),
  })
}

export async function loginUser(email, password) {
  const tokenData = await apiFetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })

  const user = await apiFetch('/api/auth/me', {
    token: tokenData.access_token,
  })

  return {
    ...tokenData,
    user,
  }
}

export async function getCurrentUser(token = getAuthToken()) {
  if (!token) {
    throw new Error('Требуется авторизация')
  }

  return apiFetch('/api/auth/me', { token })
}

export function logoutUser() {
  localStorage.removeItem('user')
  sessionStorage.removeItem('user')
}
