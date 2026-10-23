import { apiFetch } from './client'

export interface AdminDashboard {
  users_total: number
  admins: number
  directors: number
  researchers: number
  analyses_total: number
  tasks_total: number
  tasks_pending: number
  tasks_processing: number
  tasks_success: number
  tasks_failure: number
  active_invites: number
}

export interface AdminTask {
  id: number
  task_id: string
  status: string
  original_filename: string
  user_id: number
  result_id: number | null
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface AdminInvite {
  id: number
  code: string
  director_id: number
  is_active: boolean
  created_at: string
  expires_at: string
}

export interface AuditLog {
  id: number
  actor_id: number | null
  action: string
  target_type: string
  target_id: number | null
  details: Record<string, unknown> | null
  created_at: string
}

export interface PageParams {
  limit?: number
  offset?: number
}

function query(params: Record<string, string | number | undefined>) {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') search.set(key, String(value))
  }
  return search.size ? `?${search}` : ''
}

export function getAdminDashboard(signal?: AbortSignal) {
  return apiFetch<AdminDashboard>('/api/admin/dashboard', { signal })
}
export function getAdminTasks(params: PageParams & { status?: string } = {}, signal?: AbortSignal) {
  return apiFetch<AdminTask[]>(`/api/admin/tasks${query({ ...params })}`, { signal })
}
export function getAdminInvites(params: PageParams = {}, signal?: AbortSignal) {
  return apiFetch<AdminInvite[]>(`/api/admin/invites${query({ ...params })}`, { signal })
}
export function getAuditLogs(
  params: PageParams & { action?: string; date?: string } = {},
  signal?: AbortSignal,
) {
  return apiFetch<AuditLog[]>(`/api/logs${query({ ...params })}`, { signal })
}
