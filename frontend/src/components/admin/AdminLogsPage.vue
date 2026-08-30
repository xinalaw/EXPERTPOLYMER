<script setup>
import { onMounted, ref } from 'vue'
import { getAuditLogs } from '@/api/admin'
const logs = ref([]); const action = ref(''); const selectedDate = ref(''); const loading = ref(false); const error = ref('')
async function load() { loading.value = true; error.value = ''; try { logs.value = await getAuditLogs({ action: action.value, date: selectedDate.value }) } catch (e) { error.value = e.message } finally { loading.value = false } }
const date = (value) => new Date(value).toLocaleString('ru-RU')
const details = (value) => value ? JSON.stringify(value) : '—'
onMounted(load)
</script>

<template><section class="admin-content">
  <div class="admin-toolbar"><input v-model.trim="action" class="admin-input" placeholder="Точное имя действия"><input v-model="selectedDate" type="date" class="admin-input"><button class="admin-button" :disabled="loading" @click="load">Применить</button></div>
  <p v-if="error" class="admin-message admin-error">{{ error }}</p><p v-else-if="loading" class="admin-message">Загрузка журнала…</p>
  <div v-else class="admin-table-wrap"><table class="admin-table"><thead><tr><th>Время</th><th>Действие</th><th>Actor ID</th><th>Объект</th><th>Детали</th></tr></thead>
    <tbody><tr v-for="log in logs" :key="log.id"><td>{{ date(log.created_at) }}</td><td><span class="admin-badge">{{ log.action }}</span></td><td>{{ log.actor_id ?? 'system' }}</td><td>{{ log.target_type }} #{{ log.target_id ?? '—' }}</td><td class="admin-code">{{ details(log.details) }}</td></tr>
    <tr v-if="!logs.length"><td colspan="5" class="admin-muted">Записей нет</td></tr></tbody></table></div>
</section></template>
