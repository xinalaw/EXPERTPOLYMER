<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getAuditLogs } from '@/api/admin'
import { useAdminList } from '@/composables/useAdminList'
import { adminDate } from '@/utils/admin'
import AdminPagination from './AdminPagination.vue'
const action = ref('')
const selectedDate = ref('')
const filters = ref({ action: '', date: '' })
const {
  rows: logs,
  loading,
  error,
  page,
  hasNext,
  load,
} = useAdminList((offset, limit, signal) =>
  getAuditLogs({ ...filters.value, offset, limit }, signal),
)
function apply() {
  filters.value = { action: action.value, date: selectedDate.value }
  void load()
}
onMounted(() => load())
</script>
<template>
  <section class="panel" aria-labelledby="admin-logs-title" :aria-busy="loading">
    <h2 id="admin-logs-title">Журнал действий</h2>
    <form class="admin-toolbar" @submit.prevent="apply">
      <div class="form-field">
        <label for="log-action">Имя действия</label
        ><input
          id="log-action"
          v-model.trim="action"
          placeholder="Например, CHANGE_USER_ROLE"
        /><span class="field-hint">Точное имя действия; пустое поле — все действия.</span>
      </div>
      <div class="form-field">
        <label for="log-date">Дата действия</label
        ><input id="log-date" v-model="selectedDate" type="date" />
      </div>
      <button class="btn btn-secondary" :disabled="loading">Применить</button>
    </form>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-else-if="loading" role="status">Загрузка журнала…</p>
    <div v-else class="admin-table-wrap" role="region" aria-label="Записи журнала" tabindex="0">
      <table class="admin-table">
        <thead>
          <tr>
            <th scope="col">Время</th>
            <th scope="col">Действие</th>
            <th scope="col">Инициатор</th>
            <th scope="col">Объект</th>
            <th scope="col">Детали</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ adminDate(log.created_at) }}</td>
            <td>
              <span class="admin-badge">{{ log.action }}</span>
            </td>
            <td>{{ log.actor_id === null ? 'Система' : '#' + log.actor_id }}</td>
            <td>{{ log.target_type }} #{{ log.target_id ?? '—' }}</td>
            <td class="admin-code">{{ log.details ? JSON.stringify(log.details) : '—' }}</td>
          </tr>
          <tr v-if="!logs.length">
            <td colspan="5" class="muted">Записей нет</td>
          </tr>
        </tbody>
      </table>
    </div>
    <AdminPagination :page="page" :has-next="hasNext" :loading="loading" @change="load" />
  </section>
</template>
