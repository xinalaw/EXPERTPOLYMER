import { reactive, readonly } from 'vue'

const state = reactive({ reducedMotion: false, pageSize: 20 })
try {
  const saved = JSON.parse(localStorage.getItem('expert-polymer-preferences') || '{}')
  state.reducedMotion = saved.reducedMotion === true
  if ([10, 20, 50].includes(saved.pageSize)) state.pageSize = saved.pageSize
} catch {
  /* Defaults work even if storage is unavailable. */
}

function apply() {
  document.documentElement.dataset.reducedMotion = String(state.reducedMotion)
}
apply()
export const preferences = readonly(state)
export function updatePreferences(values: { reducedMotion: boolean; pageSize: number }): boolean {
  state.reducedMotion = values.reducedMotion
  state.pageSize = [10, 20, 50].includes(values.pageSize) ? values.pageSize : 20
  apply()
  try {
    localStorage.setItem('expert-polymer-preferences', JSON.stringify(state))
    return true
  } catch {
    return false
  }
}
