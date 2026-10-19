<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { getAdminDashboard } from '@/api/admin'
import { useAdminResource } from '@/composables/useAdminResource'
const { data: stats, loading, error, load } = useAdminResource(getAdminDashboard)
const metrics = computed(() =>
  stats.value
    ? [
        ['Всего пользователей', stats.value.users_total],
        ['Администраторы', stats.value.admins],
        ['Директора', stats.value.directors],
        ['Исследователи', stats.value.researchers],
        ['Результаты анализов', stats.value.analyses_total],
        ['Все задачи', stats.value.tasks_total],
        ['Задачи в работе', stats.value.tasks_pending + stats.value.tasks_processing],
        ['Успешные задачи', stats.value.tasks_success],
        ['Ошибки задач', stats.value.tasks_failure],
        ['Активные инвайты', stats.value.active_invites],
      ]
    : [],
)
onMounted(load)
</script>
<template>
  <section class="panel" aria-labelledby="admin-overview-title" :aria-busy="loading">
    <h2 id="admin-overview-title">Обзор системы</h2>
    <div class="admin-toolbar">
      <button class="btn btn-secondary" :disabled="loading" @click="load">Обновить</button>
    </div>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-else-if="loading" role="status">Загрузка статистики…</p>
    <dl v-else class="admin-stats">
      <div v-for="[label, value] in metrics" :key="label" class="admin-stat">
        <dt>{{ label }}</dt>
        <dd>{{ value }}</dd>
      </div>
    </dl>
  </section>
</template>
