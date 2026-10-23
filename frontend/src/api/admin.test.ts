import { beforeEach, expect, it, vi } from 'vitest'
import { getAdminTasks, getAuditLogs } from './admin'
import { getAnalysisHistory } from './analysis'
import { setAuthToken } from './client'
import { changeUserDirector, getAllUsers } from './users'

const fetchMock = vi.fn<typeof fetch>()
beforeEach(() => {
  setAuthToken('admin-token')
  fetchMock.mockReset().mockResolvedValue(new Response('[]', { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
})
it('uses the verified shared token and the server history filter name', async () => {
  await getAnalysisHistory({ user_id: 12, date: '2026-10-19', limit: 26, offset: 25 })
  const url = new URL(String(fetchMock.mock.lastCall?.[0]), 'http://localhost')
  expect(url.searchParams.get('user_id')).toBe('12')
  expect(url.searchParams.has('userId')).toBe(false)
  expect(new Headers(fetchMock.mock.lastCall?.[1]?.headers).get('Authorization')).toBe(
    'Bearer admin-token',
  )
})
it('encodes task and audit filters and preserves pagination', async () => {
  await getAdminTasks({ status: 'FAILURE', limit: 26, offset: 25 })
  expect(fetchMock.mock.lastCall?.[0]).toBe('/api/admin/tasks?status=FAILURE&limit=26&offset=25')
  fetchMock.mockResolvedValueOnce(new Response('[]'))
  await getAuditLogs({ action: 'A&B', date: '2026-10-19' })
  expect(fetchMock.mock.lastCall?.[0]).toBe('/api/logs?action=A%26B&date=2026-10-19')
})
it('reads beyond the first user page so every director can be assigned', async () => {
  const users = Array.from({ length: 100 }, (_, id) => ({ id }))
  fetchMock
    .mockResolvedValueOnce(new Response(JSON.stringify(users)))
    .mockResolvedValueOnce(new Response('[{"id":101,"role":"director"}]'))
  expect(await getAllUsers()).toHaveLength(101)
  expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
    '/api/users?limit=100&offset=0',
    '/api/users?limit=100&offset=100',
  ])
})
it('serializes an unassigned director as null', async () => {
  fetchMock.mockResolvedValueOnce(new Response('{}'))
  await changeUserDirector(2, null)
  expect(fetchMock.mock.lastCall?.[0]).toBe('/api/users/2/director')
  expect(fetchMock.mock.lastCall?.[1]).toMatchObject({
    method: 'PATCH',
    body: '{"director_id":null}',
  })
})
