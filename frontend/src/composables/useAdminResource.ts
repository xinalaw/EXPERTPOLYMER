import { onBeforeUnmount, ref, shallowRef } from 'vue'

export function useAdminResource<T>(fetcher: (signal: AbortSignal) => Promise<T>) {
  const data = shallowRef<T | null>(null)
  const loading = ref(false)
  const error = ref('')
  let version = 0
  let controller: AbortController | undefined

  async function load() {
    controller?.abort()
    const request = ++version
    controller = new AbortController()
    loading.value = true
    error.value = ''
    data.value = null
    try {
      const response = await fetcher(controller.signal)
      if (request === version) data.value = response
    } catch (cause) {
      if (request === version && !(cause instanceof Error && cause.name === 'AbortError'))
        error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить данные'
    } finally {
      if (request === version) loading.value = false
    }
  }

  onBeforeUnmount(() => {
    version++
    controller?.abort()
  })
  return { data, loading, error, load }
}
