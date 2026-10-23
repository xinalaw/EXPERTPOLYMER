<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getAnalysisHistory } from '@/api/analysis'
import { useAdminList } from '@/composables/useAdminList'
import { adminDate } from '@/utils/admin'
import AdminPagination from './AdminPagination.vue'
const selectedDate = ref('')
const userId = ref('')
const filters = ref<{ date: string; user_id?: number }>({ date: '' })
const {
  rows: results,
  loading,
  error,
  page,
  hasNext,
  load,
} = useAdminList((offset, limit, signal) =>
  getAnalysisHistory({ ...filters.value, offset, limit }, signal),
)
function apply() {
  filters.value = {
    date: selectedDate.value,
    user_id: userId.value ? Number(userId.value) : undefined,
  }
  void load()
}
onMounted(() => load())
</script>
<template>
  <section class="panel" aria-labelledby="admin-history-title" :aria-busy="loading">
    <h2 id="admin-history-title">История анализов</h2>
    <form class="admin-toolbar" @submit.prevent="apply">
      <div class="form-field">
        <label for="history-user">ID пользователя</label
        ><input
          id="history-user"
          v-model="userId"
          type="number"
          min="1"
          step="1"
          placeholder="Все пользователи"
        />
      </div>
      <div class="form-field">
        <label for="history-date">Дата анализа</label
        ><input id="history-date" v-model="selectedDate" type="date" />
      </div>
      <button class="btn btn-secondary" :disabled="loading">Применить</button>
    </form>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-else-if="loading" role="status">Загрузка истории…</p>
    <div v-else class="admin-table-wrap" role="region" aria-label="Список анализов" tabindex="0">
      <table class="admin-table">
        <thead>
          <tr>
            <th scope="col">Дата</th>
            <th scope="col">ID</th>
            <th scope="col">Пользователь</th>
            <th scope="col">Файл</th>
            <th scope="col">Результат</th>
            <th scope="col">Уверенность</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in results" :key="result.id">
            <td>{{ adminDate(result.created_at) }}</td>
            <td>#{{ result.id }}</td>
            <td>#{{ result.user_id }}</td>
            <td>{{ result.original_filename }}</td>
            <td>{{ result.result }}</td>
            <td>
              {{ result.confidence == null ? '—' : Math.round(result.confidence * 100) + '%' }}
            </td>
          </tr>
          <tr v-if="!results.length">
            <td colspan="6" class="muted">Результатов нет</td>
          </tr>
        </tbody>
      </table>
    </div>
    <AdminPagination :page="page" :has-next="hasNext" :loading="loading" @change="load" />
  </section>
</template>
