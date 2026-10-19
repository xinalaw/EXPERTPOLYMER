import { computed, ref } from 'vue'
import { useAdminResource } from './useAdminResource'

export function useAdminList<T>(
  fetcher: (offset: number, limit: number, signal: AbortSignal) => Promise<T[]>,
) {
  const page = ref(1)
  const pageSize = 25
  let version = 0
  const resource = useAdminResource((signal) =>
    fetcher((page.value - 1) * pageSize, pageSize + 1, signal),
  )
  const rows = computed(() => resource.data.value?.slice(0, pageSize) || [])
  const hasNext = computed(() => (resource.data.value?.length || 0) > pageSize)
  async function load(nextPage = 1) {
    const request = ++version
    page.value = Math.max(1, nextPage)
    await resource.load()
    if (request !== version) return
    if (resource.data.value?.length === 0 && page.value > 1) {
      page.value = 1
      await resource.load()
    }
  }
  return { rows, loading: resource.loading, error: resource.error, hasNext, page, load }
}
