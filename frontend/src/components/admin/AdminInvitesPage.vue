<script setup lang="ts">
import { onMounted } from 'vue'
import { getAdminInvites, type AdminInvite } from '@/api/admin'
import { useAdminList } from '@/composables/useAdminList'
import { adminDate } from '@/utils/admin'
import AdminPagination from './AdminPagination.vue'
const {
  rows: invites,
  loading,
  error,
  page,
  hasNext,
  load,
} = useAdminList((offset, limit, signal) => getAdminInvites({ offset, limit }, signal))
const state = (invite: AdminInvite) =>
  !invite.is_active ? 'Неактивен' : new Date(invite.expires_at) <= new Date() ? 'Истёк' : 'Активен'
onMounted(() => load())
</script>
<template>
  <section class="panel" aria-labelledby="admin-invites-title" :aria-busy="loading">
    <h2 id="admin-invites-title">Приглашения директоров</h2>
    <div class="admin-toolbar">
      <button class="btn btn-secondary" :disabled="loading" @click="load(page)">Обновить</button>
    </div>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-else-if="loading" role="status">Загрузка инвайтов…</p>
    <div v-else class="admin-table-wrap" role="region" aria-label="Список приглашений" tabindex="0">
      <table class="admin-table">
        <thead>
          <tr>
            <th scope="col">Код</th>
            <th scope="col">ID директора</th>
            <th scope="col">Создан</th>
            <th scope="col">Истекает</th>
            <th scope="col">Состояние</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="invite in invites" :key="invite.id">
            <td class="admin-code">{{ invite.code }}</td>
            <td>#{{ invite.director_id }}</td>
            <td>{{ adminDate(invite.created_at) }}</td>
            <td>{{ adminDate(invite.expires_at) }}</td>
            <td>
              <span class="admin-badge">{{ state(invite) }}</span>
            </td>
          </tr>
          <tr v-if="!invites.length">
            <td colspan="5" class="muted">Инвайтов нет</td>
          </tr>
        </tbody>
      </table>
    </div>
    <AdminPagination :page="page" :has-next="hasNext" :loading="loading" @change="load" />
  </section>
</template>
