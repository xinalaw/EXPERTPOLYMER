<script setup>
import { onMounted, ref } from 'vue'
import { getAdminInvites } from '@/api/admin'
const invites = ref([]); const error = ref(''); const loading = ref(false)
async function load() { loading.value = true; error.value = ''; try { invites.value = await getAdminInvites() } catch (e) { error.value = e.message } finally { loading.value = false } }
const date = (value) => new Date(value).toLocaleString('ru-RU')
const state = (invite) => !invite.is_active ? 'Неактивен' : new Date(invite.expires_at) <= new Date() ? 'Истёк' : 'Активен'
onMounted(load)
</script>

<template><section class="admin-content">
  <div class="admin-toolbar"><button class="admin-button" :disabled="loading" @click="load">Обновить</button></div>
  <p v-if="error" class="admin-message admin-error">{{ error }}</p><p v-else-if="loading" class="admin-message">Загрузка инвайтов…</p>
  <div v-else class="admin-table-wrap"><table class="admin-table"><thead><tr><th>Код</th><th>Director ID</th><th>Создан</th><th>Истекает</th><th>Состояние</th></tr></thead>
    <tbody><tr v-for="invite in invites" :key="invite.id"><td class="admin-code">{{ invite.code }}</td><td>{{ invite.director_id }}</td><td>{{ date(invite.created_at) }}</td><td>{{ date(invite.expires_at) }}</td><td><span class="admin-badge">{{ state(invite) }}</span></td></tr>
    <tr v-if="!invites.length"><td colspan="5" class="admin-muted">Инвайтов нет</td></tr></tbody></table></div>
</section></template>
