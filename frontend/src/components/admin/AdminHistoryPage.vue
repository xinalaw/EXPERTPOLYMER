<script setup>
import { onMounted, ref } from 'vue'
import { getAnalysisHistory } from '@/api/analysis'
const results = ref([]); const selectedDate = ref(''); const userId = ref(''); const loading = ref(false); const error = ref('')
async function load() { loading.value = true; error.value = ''; try { results.value = await getAnalysisHistory({ date: selectedDate.value, userId: userId.value || null, limit: 100 }) } catch (e) { error.value = e.message } finally { loading.value = false } }
const date = (value) => new Date(value).toLocaleString('ru-RU')
onMounted(load)
</script>

<template><section class="admin-content">
  <div class="admin-toolbar"><input v-model="userId" type="number" min="1" class="admin-input" placeholder="User ID"><input v-model="selectedDate" type="date" class="admin-input"><button class="admin-button" :disabled="loading" @click="load">Применить</button></div>
  <p v-if="error" class="admin-message admin-error">{{ error }}</p><p v-else-if="loading" class="admin-message">Загрузка истории…</p>
  <div v-else class="admin-table-wrap"><table class="admin-table"><thead><tr><th>Дата</th><th>ID</th><th>Пользователь</th><th>Файл</th><th>Результат</th><th>Уверенность</th></tr></thead>
    <tbody><tr v-for="result in results" :key="result.id"><td>{{ date(result.created_at) }}</td><td>#{{ result.id }}</td><td>#{{ result.user_id }}</td><td>{{ result.original_filename }}</td><td>{{ result.result }}</td><td>{{ Math.round(result.confidence * 100) }}%</td></tr>
    <tr v-if="!results.length"><td colspan="6" class="admin-muted">Результатов нет</td></tr></tbody></table></div>
</section></template>
