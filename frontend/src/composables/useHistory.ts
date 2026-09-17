import { onBeforeUnmount, ref } from 'vue'
import { getAnalysisHistory } from '@/api/analysis'
import type { AnalysisResult } from '@/api/types'

export function useHistory() {
  const results = ref<AnalysisResult[]>([])
  const loading = ref(false)
  const error = ref('')
  const hasNext = ref(false)
  const offset = ref(0)
  let controller: AbortController | null = null
  let version = 0
  async function load(date: string, page: number, size: number) {
    controller?.abort()
    const request = ++version
    controller = new AbortController()
    loading.value = true
    error.value = ''
    results.value = []
    hasNext.value = false
    try {
      let nextOffset = Math.max(0, page - 1) * size
      let rows = await getAnalysisHistory(
        { date, limit: size + 1, offset: nextOffset },
        controller.signal,
      )
      if (request !== version) return
      // Deleting the last item (or a stale bookmarked page) should not strand the user.
      if (!rows.length && nextOffset > 0) {
        nextOffset = 0
        rows = await getAnalysisHistory({ date, limit: size + 1, offset: 0 }, controller.signal)
      }
      if (request !== version) return
      results.value = rows.slice(0, size)
      hasNext.value = rows.length > size
      offset.value = nextOffset
    } catch (cause) {
      if (request !== version) return
      if (!(cause instanceof Error && cause.name === 'AbortError')) {
        error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить историю'
      }
    } finally {
      if (request === version) loading.value = false
    }
  }
  onBeforeUnmount(() => {
    version++
    controller?.abort()
  })
  return { results, loading, error, hasNext, offset, load }
}
