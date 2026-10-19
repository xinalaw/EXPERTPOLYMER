import { computed, readonly, ref } from 'vue'
import { analyzeImage } from '@/api/analysis'
import type { AnalysisResult } from '@/api/types'
import { validateImage } from '@/utils/files'

// One draft survives navigation; it is cleared whenever the session changes.
const file = ref<File | null>(null)
const preview = ref('')
const result = ref<AnalysisResult | null>(null)
const phase = ref<'idle' | 'validating' | 'running' | 'complete'>('idle')
const error = ref('')
let controller: AbortController | null = null
let version = 0

export function resetAnalysis() {
  version++
  controller?.abort()
  controller = null
  if (preview.value) URL.revokeObjectURL(preview.value)
  file.value = null
  preview.value = ''
  result.value = null
  error.value = ''
  phase.value = 'idle'
}

async function selectFile(candidate: File) {
  if (phase.value === 'running') return
  resetAnalysis()
  const request = ++version
  phase.value = 'validating'
  try {
    const message = await validateImage(candidate)
    if (version !== request) return
    if (message) {
      error.value = message
      return
    }
    file.value = candidate
    preview.value = URL.createObjectURL(candidate)
  } catch {
    if (version === request) error.value = 'Не удалось прочитать файл. Выберите его повторно.'
  } finally {
    if (version === request) phase.value = 'idle'
  }
}

async function start() {
  if (!file.value || phase.value !== 'idle') return
  const request = ++version
  controller = new AbortController()
  phase.value = 'running'
  error.value = ''
  try {
    const response = await analyzeImage(file.value, controller.signal)
    if (version !== request) return
    result.value = response
    phase.value = 'complete'
  } catch (cause) {
    if (version !== request) return
    error.value = cause instanceof Error ? cause.message : 'Ошибка анализа'
    phase.value = 'idle'
  } finally {
    if (version === request) controller = null
  }
}

function cancel() {
  version++
  controller?.abort()
  controller = null
  phase.value = 'idle'
  error.value =
    'Ожидание остановлено. Сервер может завершить анализ — проверьте историю перед повторным запуском.'
}

export function useAnalysis() {
  return {
    file: readonly(file),
    preview: readonly(preview),
    result: readonly(result),
    phase: readonly(phase),
    error: readonly(error),
    busy: computed(() => ['running', 'validating'].includes(phase.value)),
    selectFile,
    start,
    cancel,
    reset: resetAnalysis,
  }
}
