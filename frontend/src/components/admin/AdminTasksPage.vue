<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getAdminTasks } from '@/api/admin'
import { useAdminList } from '@/composables/useAdminList'
import { adminDate } from '@/utils/admin'
import AdminPagination from './AdminPagination.vue'
const status = ref('')
const appliedStatus = ref('')
const {
  rows: tasks,
  loading,
  error,
  page,
  hasNext,
  load,
} = useAdminList((offset, limit, signal) =>
  getAdminTasks({ status: appliedStatus.value, offset, limit }, signal),
)
function apply() {
  appliedStatus.value = status.value
  void load()
}
onMounted(() => load())
</script>
<template>
  <section class="panel" aria-labelledby="admin-tasks-title" :aria-busy="loading">
    <h2 id="admin-tasks-title">Задачи анализа</h2>
    <form class="admin-toolbar" @submit.prevent="apply">
      <div class="form-field">
        <label for="task-status">Статус задачи</label
        ><select id="task-status" v-model="status">
          <option value="">Все статусы</option>
          <option>PENDING</option>
          <option>PROCESSING</option>
          <option>RETRY</option>
          <option>SUCCESS</option>
          <option>FAILURE</option>
        </select>
      </div>
      <button class="btn btn-secondary" :disabled="loading">Применить</button>
    </form>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-else-if="loading" role="status">Загрузка задач…</p>
    <div v-else class="admin-table-wrap" role="region" aria-label="Список задач" tabindex="0">
      <table class="admin-table">
        <thead>
          <tr>
            <th scope="col">Создана</th>
            <th scope="col">Задача</th>
            <th scope="col">Файл</th>
            <th scope="col">Пользователь</th>
            <th scope="col">Статус</th>
            <th scope="col">Результат / ошибка</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>{{ adminDate(task.created_at) }}</td>
            <td class="admin-code">{{ task.task_id }}</td>
            <td>{{ task.original_filename }}</td>
            <td>#{{ task.user_id }}</td>
            <td>
              <span class="admin-badge">{{ task.status }}</span>
            </td>
            <td>{{ task.error_message || (task.result_id ? '#' + task.result_id : '—') }}</td>
          </tr>
          <tr v-if="!tasks.length">
            <td colspan="6" class="muted">Задач нет</td>
          </tr>
        </tbody>
      </table>
    </div>
    <AdminPagination :page="page" :has-next="hasNext" :loading="loading" @change="load" />
  </section>
</template>
