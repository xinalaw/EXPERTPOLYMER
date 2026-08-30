import { apiFetch } from './client'
import { getAuthToken } from './auth'

export function getUsers({ limit = 100, offset = 0 } = {}) {
  return apiFetch(`/api/users?limit=${limit}&offset=${offset}`, {
    token: getAuthToken(),
  })
}

export function changeUserRole(userId, role) {
  return apiFetch(`/api/users/${userId}/role`, {
    method: 'PATCH',
    token: getAuthToken(),
    body: JSON.stringify({ role }),
  })
}

export function changeUserDirector(userId, directorId) {
  return apiFetch(`/api/users/${userId}/director`, {
    method: 'PATCH',
    token: getAuthToken(),
    body: JSON.stringify({ director_id: directorId }),
  })
}
