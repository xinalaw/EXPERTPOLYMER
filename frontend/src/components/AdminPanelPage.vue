<script setup>
import { ref } from 'vue'
import AdminDashboardPage from './admin/AdminDashboardPage.vue'
import AdminHistoryPage from './admin/AdminHistoryPage.vue'
import AdminInvitesPage from './admin/AdminInvitesPage.vue'
import AdminLogsPage from './admin/AdminLogsPage.vue'
import AdminTasksPage from './admin/AdminTasksPage.vue'
import AdminUsersPage from './AdminUsersPage.vue'

defineProps({ currentUserId: { type: Number, default: null } })

const activeTab = ref('dashboard')
const tabs = [
  ['dashboard', 'Обзор'],
  ['users', 'Пользователи'],
  ['history', 'История анализов'],
  ['tasks', 'Задачи'],
  ['invites', 'Инвайты'],
  ['logs', 'Журнал действий'],
]
</script>

<template>
  <main class="admin-shell container">
    <header class="admin-header">
      <div><h1>Панель администратора</h1><p>Управление системой и контроль операций.</p></div>
    </header>
    <nav class="admin-tabs" aria-label="Разделы панели администратора">
      <button
        v-for="tab in tabs"
        :key="tab[0]"
        :class="{ active: activeTab === tab[0] }"
        @click="activeTab = tab[0]"
      >{{ tab[1] }}</button>
    </nav>
    <AdminDashboardPage v-if="activeTab === 'dashboard'" />
    <AdminUsersPage v-else-if="activeTab === 'users'" :current-user-id="currentUserId" />
    <AdminHistoryPage v-else-if="activeTab === 'history'" />
    <AdminTasksPage v-else-if="activeTab === 'tasks'" />
    <AdminInvitesPage v-else-if="activeTab === 'invites'" />
    <AdminLogsPage v-else-if="activeTab === 'logs'" />
  </main>
</template>

<style scoped>
.admin-shell { padding-top: 2.5rem; padding-bottom: 4rem; }
.admin-header h1 { color: #1e3c72; font-size: 2.35rem; }
.admin-tabs { display: flex; gap: .5rem; overflow-x: auto; margin: 1.5rem 0; padding-bottom: .5rem; }
.admin-tabs button { flex: 0 0 auto; border: 1px solid #c8d2df; border-radius: 8px; padding: .7rem 1rem; color: #2a4365; background: #fff; cursor: pointer; }
.admin-tabs button.active { color: #fff; border-color: #2a5298; background: #2a5298; }
</style>
