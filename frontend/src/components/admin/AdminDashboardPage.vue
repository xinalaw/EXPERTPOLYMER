<script setup>
import { onMounted, ref } from 'vue'
import { getAdminDashboard } from '@/api/admin'

const stats = ref(null)
const error = ref('')
async function load() {
  error.value = ''
  try { stats.value = await getAdminDashboard() } catch (requestError) { error.value = requestError.message }
}
onMounted(load)
</script>

<template>
  <section class="admin-content">
    <div class="admin-toolbar"><button class="admin-button" @click="load">Обновить</button></div>
    <p v-if="error" class="admin-message admin-error">{{ error }}</p>
    <p v-else-if="!stats" class="admin-message">Загрузка статистики…</p>
    <div v-else class="admin-stats">
      <article class="admin-stat">Всего пользователей<strong>{{ stats.users_total }}</strong></article>
      <article class="admin-stat">Администраторы<strong>{{ stats.admins }}</strong></article>
      <article class="admin-stat">Директора<strong>{{ stats.directors }}</strong></article>
      <article class="admin-stat">Исследователи<strong>{{ stats.researchers }}</strong></article>
      <article class="admin-stat">Результаты анализов<strong>{{ stats.analyses_total }}</strong></article>
      <article class="admin-stat">Все задачи<strong>{{ stats.tasks_total }}</strong></article>
      <article class="admin-stat">Задачи в работе<strong>{{ stats.tasks_pending + stats.tasks_processing }}</strong></article>
      <article class="admin-stat">Ошибки задач<strong>{{ stats.tasks_failure }}</strong></article>
      <article class="admin-stat">Активные инвайты<strong>{{ stats.active_invites }}</strong></article>
    </div>
  </section>
</template>
