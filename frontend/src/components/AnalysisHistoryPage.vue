<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deleteAnalysisResult } from '@/api/analysis'
import type { AnalysisResult as Result } from '@/api/types'
import { auth } from '@/stores/auth'
import { preferences } from '@/stores/preferences'
import { useHistory } from '@/composables/useHistory'
import { downloadReport, formatDate, formatPercent } from '@/utils/files'
import AnalysisResult from './analysis/AnalysisResult.vue'
import AppDialog from './ui/AppDialog.vue'

const route = useRoute()
const router = useRouter()
const { results, loading, error, hasNext, offset, load } = useHistory()
const date = computed(() =>
  typeof route.query.date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(route.query.date)
    ? route.query.date
    : '',
)
const page = computed(() => {
  const value = Number(route.query.page)
  return Number.isSafeInteger(value) && value > 0 && value < 1000000 ? value : 1
})
const expanded = ref<number[]>([])
const pendingDelete = ref<Result | null>(null)
const deleting = ref(false)
const actionError = ref('')
const notice = ref('')
function requestDelete(result: Result) {
  pendingDelete.value = result
  actionError.value = ''
}
let refreshVersion = 0
onBeforeUnmount(() => {
  refreshVersion++
})
function setPage(value: number) {
  return router.push({ query: { ...route.query, page: value > 1 ? String(value) : undefined } })
}
function setDate(event: Event) {
  router.push({ query: { date: (event.target as HTMLInputElement).value || undefined } })
}
async function refresh() {
  const request = ++refreshVersion
  expanded.value = []
  await load(date.value, page.value, preferences.pageSize)
  if (request !== refreshVersion) return
  if (!error.value && offset.value === 0 && page.value > 1) {
    await router.replace({ query: { ...route.query, page: undefined } })
  }
}
watch([date, page, () => preferences.pageSize], refresh, { immediate: true })
function toggle(id: number) {
  expanded.value = expanded.value.includes(id)
    ? expanded.value.filter((value) => value !== id)
    : [...expanded.value, id]
}
function download(result: Result) {
  actionError.value = ''
  try {
    downloadReport(result)
  } catch {
    actionError.value = 'Не удалось скачать отчёт. Повторите попытку.'
  }
}
function canDelete(result: Result) {
  return ['admin', 'director'].includes(auth.user?.role || '') || result.user_id === auth.user?.id
}
async function confirmDelete() {
  if (!pendingDelete.value || deleting.value) return
  deleting.value = true
  actionError.value = ''
  try {
    await deleteAnalysisResult(pendingDelete.value.id)
    pendingDelete.value = null
    notice.value = 'Анализ удалён.'
    await refresh()
    await nextTick()
    document.getElementById('history-heading')?.focus()
  } catch (cause) {
    actionError.value = cause instanceof Error ? cause.message : 'Не удалось удалить анализ'
  } finally {
    deleting.value = false
  }
}
</script>
<template>
  <div class="page-shell">
    <header class="page-heading">
      <h1 id="history-heading" tabindex="-1">История анализов</h1>
      <p>Результаты исследований, доступные вашей учётной записи.</p>
    </header>
    <div class="panel filters">
      <div class="form-field">
        <label for="history-date">Фильтр по дате</label
        ><input id="history-date" type="date" :value="date" @change="setDate" />
      </div>
      <button class="btn btn-secondary" :disabled="loading" @click="refresh">Обновить</button>
      <RouterLink v-if="date" to="/history" class="btn btn-secondary">Сбросить фильтр</RouterLink>
    </div>
    <p v-if="notice" class="notice" role="status">{{ notice }}</p>
    <p v-if="actionError && !pendingDelete" class="notice error" role="alert">{{ actionError }}</p>
    <div v-if="error" class="notice error" role="alert">
      <p>{{ error }}</p>
      <button class="btn btn-secondary" @click="refresh">Повторить</button>
    </div>
    <p v-if="loading" class="panel" role="status">Загрузка истории…</p>
    <section v-else-if="!error && !results.length" class="panel">
      <h2>Анализы не найдены</h2>
      <p>
        {{
          date
            ? 'За выбранную дату результатов нет. Выберите другую дату.'
            : 'Выполните первый анализ, чтобы увидеть результат здесь.'
        }}
      </p>
      <RouterLink class="btn btn-primary" to="/analysis">Начать анализ</RouterLink>
    </section>
    <div v-else-if="!error" class="history-list">
      <article v-for="result in results" :key="result.id" class="panel history-card">
        <h2>
          <button
            class="card-toggle"
            :aria-expanded="expanded.includes(result.id)"
            :aria-controls="'result-' + result.id"
            @click="toggle(result.id)"
          >
            <span>{{ result.original_filename }}</span
            ><span aria-hidden="true">{{ expanded.includes(result.id) ? '−' : '+' }}</span>
          </button>
        </h2>
        <p class="muted">
          {{ formatDate(result.created_at) }} · Уверенность: {{ formatPercent(result.confidence) }}
        </p>
        <div v-if="expanded.includes(result.id)" :id="'result-' + result.id">
          <AnalysisResult :result="result" />
          <div class="actions">
            <button class="btn btn-primary" @click="download(result)">Скачать отчёт (JSON)</button
            ><button
              v-if="canDelete(result)"
              class="btn btn-danger"
              :disabled="deleting"
              @click="requestDelete(result)"
            >
              Удалить анализ
            </button>
          </div>
        </div>
      </article>
    </div>
    <nav
      v-if="!loading && !error && (offset > 0 || hasNext)"
      class="pagination"
      aria-label="Страницы истории"
    >
      <button class="btn btn-secondary" :disabled="offset === 0" @click="setPage(page - 1)">
        Назад
      </button>
      <span aria-live="polite">{{ offset + 1 }}–{{ offset + results.length }}</span>
      <button class="btn btn-secondary" :disabled="!hasNext" @click="setPage(page + 1)">
        Вперёд
      </button>
    </nav>
    <AppDialog
      :open="!!pendingDelete"
      title="Удалить анализ?"
      :busy="deleting"
      @close="pendingDelete = null"
    >
      <p>
        Результат «{{ pendingDelete?.original_filename }}» и его изображения будут удалены без
        возможности восстановления.
      </p>
      <p v-if="actionError" class="notice error" role="alert">{{ actionError }}</p>
      <div class="actions">
        <button
          autofocus
          class="btn btn-secondary"
          :disabled="deleting"
          @click="pendingDelete = null"
        >
          Отмена</button
        ><button class="btn btn-danger" :disabled="deleting" @click="confirmDelete">
          {{ deleting ? 'Удаление…' : 'Удалить' }}
        </button>
      </div>
    </AppDialog>
  </div>
</template>
<style scoped>
.filters {
  display: flex;
  gap: 1rem;
  align-items: end;
  flex-wrap: wrap;
}
.history-list {
  display: grid;
  gap: 1rem;
}
.history-card h2 {
  font-size: 1.15rem;
}
.card-toggle {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  border: 0;
  background: none;
  color: var(--text);
  text-align: left;
  font: inherit;
  font-weight: 700;
  padding: 0.5rem 0;
}
.card-toggle span:first-child {
  overflow-wrap: anywhere;
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>
