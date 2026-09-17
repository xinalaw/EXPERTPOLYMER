import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useHistory } from './useHistory'
import { getAnalysisHistory } from '@/api/analysis'
import type { AnalysisResult } from '@/api/types'

vi.mock('@/api/analysis', () => ({ getAnalysisHistory: vi.fn() }))
const api = vi.mocked(getAnalysisHistory)
const rows = (count: number) =>
  Array.from({ length: count }, (_, id) => ({
    id,
    user_id: 1,
    original_filename: 'image.png',
    result: 'ok',
    created_at: '2026-01-01',
  })) satisfies AnalysisResult[]
function setup() {
  let history!: ReturnType<typeof useHistory>
  mount(
    defineComponent({
      setup() {
        history = useHistory()
        return () => null
      },
    }),
  )
  return history
}
beforeEach(() => api.mockReset())
describe('history pagination', () => {
  it('uses one lookahead result, not an invented total', async () => {
    api.mockResolvedValueOnce(rows(21)).mockResolvedValueOnce(rows(2))
    const history = setup()
    await history.load('', 1, 20)
    expect(history.results.value).toHaveLength(20)
    expect(history.hasNext.value).toBe(true)
    await history.load('', 2, 20)
    expect(history.results.value).toHaveLength(2)
    expect(history.offset.value).toBe(20)
    expect(history.hasNext.value).toBe(false)
  })
  it('returns to the first page when a bookmarked page becomes empty', async () => {
    api.mockResolvedValueOnce([]).mockResolvedValueOnce(rows(3))
    const history = setup()
    await history.load('', 4, 20)
    expect(history.offset.value).toBe(0)
    expect(history.results.value).toHaveLength(3)
  })
  it('ignores an old response after changing the filter', async () => {
    let finish!: (value: AnalysisResult[]) => void
    api.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve
        }),
    )
    api.mockResolvedValueOnce(rows(1))
    const history = setup()
    const first = history.load('', 3, 20)
    await history.load('2026-09-10', 1, 20)
    finish(rows(20))
    await first
    expect(history.results.value).toHaveLength(1)
    expect(history.offset.value).toBe(0)
    expect(api.mock.calls[0]![1]?.aborted).toBe(true)
  })
  it('shows a retryable error without leaving stale results', async () => {
    api.mockRejectedValueOnce(new Error('Нет соединения'))
    const history = setup()
    await history.load('', 1, 20)
    expect(history.error.value).toBe('Нет соединения')
    expect(history.loading.value).toBe(false)
    expect(history.results.value).toHaveLength(0)
  })
})
