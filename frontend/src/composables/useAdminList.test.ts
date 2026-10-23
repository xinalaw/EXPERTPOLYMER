import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { expect, it, vi } from 'vitest'
import { useAdminList } from './useAdminList'

function setup(fetcher: (offset: number, limit: number, signal: AbortSignal) => Promise<number[]>) {
  let list!: ReturnType<typeof useAdminList<number>>
  const wrapper = mount(
    defineComponent({
      setup() {
        list = useAdminList(fetcher)
        return () => null
      },
    }),
  )
  return { list, wrapper }
}
it('pages through lists using lookahead within the backend limit', async () => {
  const fetcher = vi.fn().mockResolvedValue(Array.from({ length: 26 }, (_, i) => i))
  const { list } = setup(fetcher)
  await list.load()
  expect(fetcher).toHaveBeenLastCalledWith(0, 26, expect.any(AbortSignal))
  expect(list.rows.value).toHaveLength(25)
  expect(list.hasNext.value).toBe(true)
  fetcher.mockResolvedValue([26])
  await list.load(2)
  expect(fetcher).toHaveBeenLastCalledWith(25, 26, expect.any(AbortSignal))
  expect(list.rows.value).toEqual([26])
  expect(list.hasNext.value).toBe(false)
})
it('ignores superseded responses and aborts requests on navigation', async () => {
  let finish!: (value: number[]) => void
  const fetcher = vi
    .fn()
    .mockImplementationOnce(
      () =>
        new Promise<number[]>((resolve) => {
          finish = resolve
        }),
    )
    .mockResolvedValueOnce([42])
  const { list, wrapper } = setup(fetcher)
  const first = list.load(2)
  const firstSignal = fetcher.mock.calls[0]![2] as AbortSignal
  await list.load()
  finish([1])
  await first
  expect(firstSignal.aborted).toBe(true)
  expect(list.rows.value).toEqual([42])
  expect(list.page.value).toBe(1)
  wrapper.unmount()
  expect((fetcher.mock.calls[1]![2] as AbortSignal).aborted).toBe(true)
})
it('recovers from an empty stale page and permits retry after failure', async () => {
  const fetcher = vi
    .fn()
    .mockResolvedValueOnce([])
    .mockRejectedValueOnce(new Error('Нет соединения'))
    .mockResolvedValueOnce([7])
  const { list } = setup(fetcher)
  await list.load(3)
  expect(list.page.value).toBe(1)
  expect(list.error.value).toBe('Нет соединения')
  expect(list.rows.value).toEqual([])
  await list.load()
  expect(list.error.value).toBe('')
  expect(list.rows.value).toEqual([7])
})
