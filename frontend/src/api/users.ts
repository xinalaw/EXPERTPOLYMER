import { apiFetch } from './client'
import type { User } from './types'

export type UserRole = 'researcher' | 'director' | 'admin'

// Read every page so search and director assignment also work beyond the first 100 users.
export async function getAllUsers(signal?: AbortSignal) {
  const users: User[] = []
  for (let offset = 0; ; offset += 100) {
    const page = await apiFetch<User[]>(`/api/users?limit=100&offset=${offset}`, { signal })
    if (signal?.aborted) throw new DOMException('Запрос отменён', 'AbortError')
    users.push(...page)
    if (page.length < 100) return users
  }
}
export function changeUserRole(userId: number, role: UserRole) {
  return apiFetch<User>(`/api/users/${userId}/role`, {
    method: 'PATCH',
    body: JSON.stringify({ role }),
  })
}
export function changeUserDirector(userId: number, directorId: number | null) {
  return apiFetch<User>(`/api/users/${userId}/director`, {
    method: 'PATCH',
    body: JSON.stringify({ director_id: directorId }),
  })
}
