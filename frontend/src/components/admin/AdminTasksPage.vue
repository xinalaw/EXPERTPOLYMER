<script setup>
import { onMounted, ref } from 'vue'
import { getAdminTasks } from '@/api/admin'

const tasks = ref([])
const status = ref('')
const loading = ref(false)
const error = ref('')
async function load() {
  loading.value = true; error.value = ''
  try { tasks.value = await getAdminTasks(status.value) } catch (e) { error.value = e.message } finally { loading.value = false }
}
const date = (value) => new Date(value).toLocaleString('ru-RU')
onMounted(load)
</script>

<template>
  <section class="admin-content">
    <div class="admin-toolbar">
      <select v-model="status" class="admin-input" @change="load">
        <option value="">Все статусы</option><option>PENDING</option><option>PROCESSING</option><option>RETRY</option><option>SUCCESS</option><option>FAILURE</option>
      </select>
      <button class="admin-button" :disabled="loading" @click="load">Обновить</button>
    </div>
    <p v-if="error" class="admin-message admin-error">{{ error }}</p>
    <p v-else-if="loading" class="admin-message">Загрузка задач…</p>
    <div v-else class="admin-table-wrap"><table class="admin-table">
      <thead><tr><th>Создана</th><th>Задача</th><th>Файл</th><th>User ID</th><th>Статус</th><th>Результат / ошибка</th></tr></thead>
      <tbody><tr v-for="task in tasks" :key="task.id">
        <td>{{ date(task.created_at) }}</td><td class="admin-code">{{ task.task_id }}</td><td>{{ task.original_filename }}</td><td>{{ task.user_id }}</td>
        <td><span class="admin-badge">{{ task.status }}</span></td><td>{{ task.error_message || (task.result_id ? `#${task.result_id}` : '—') }}</td>
      </tr><tr v-if="!tasks.length"><td colspan="6" class="admin-muted">Задач нет</td></tr></tbody>
    </table></div>
  </section>
</template>
