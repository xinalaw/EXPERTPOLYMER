import { apiFetch } from './client'
import { getAuthToken } from './auth'

function adminFetch(path) {
  return apiFetch(`/api/admin${path}`, { token: getAuthToken() })
}

export function getAdminDashboard() {
  return adminFetch('/dashboard')
}

export function getAdminTasks(status = '') {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return adminFetch(`/tasks${query}`)
}

export function getAdminInvites() {
  return adminFetch('/invites')
}

export function getAuditLogs(params = {}) {
  const query = new URLSearchParams()
  if (params.action) query.set('action', params.action)
  if (params.date) query.set('date', params.date)
  query.set('limit', String(params.limit || 100))
  return apiFetch(`/api/logs?${query}`, { token: getAuthToken() })
}
