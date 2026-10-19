<script setup lang="ts">
import '@/styles/admin.css'

const tabs = [
  { name: 'admin', label: 'Обзор' },
  { name: 'admin-users', label: 'Пользователи' },
  { name: 'admin-history', label: 'История анализов' },
  { name: 'admin-tasks', label: 'Задачи' },
  { name: 'admin-invites', label: 'Инвайты' },
  { name: 'admin-logs', label: 'Журнал действий' },
]
</script>
<template>
  <div class="page-shell admin-shell">
    <header class="page-heading">
      <h1>Панель администратора</h1>
      <p>Управление пользователями и контроль работы системы.</p>
    </header>
    <nav class="admin-tabs" aria-label="Разделы панели администратора">
      <RouterLink v-for="tab in tabs" :key="tab.name" :to="{ name: tab.name }">{{
        tab.label
      }}</RouterLink>
    </nav>
    <RouterView />
  </div>
</template>
