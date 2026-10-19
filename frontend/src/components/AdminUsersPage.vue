<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { changeUserDirector, changeUserRole, getAllUsers, type UserRole } from '@/api/users'
import type { User } from '@/api/types'
import { useAdminResource } from '@/composables/useAdminResource'
import { auth } from '@/stores/auth'
import AdminPagination from './admin/AdminPagination.vue'

const { data: users, loading, error, load } = useAdminResource(getAllUsers)
const savingId = ref<number | null>(null)
const saveError = ref('')
const saved = ref('')
const query = ref('')
const page = ref(1)
const pageSize = 25
let active = true
const busy = computed(() => loading.value || savingId.value !== null)
const directors = computed(() => (users.value || []).filter((user) => user.role === 'director'))
const filteredUsers = computed(() => {
  const needle = query.value.trim().toLocaleLowerCase('ru-RU')
  return (users.value || []).filter(
    (user) =>
      !needle ||
      (user.username + ' ' + user.email + ' ' + (user.organization || ''))
        .toLocaleLowerCase('ru-RU')
        .includes(needle),
  )
})
const visibleUsers = computed(() =>
  filteredUsers.value.slice((page.value - 1) * pageSize, page.value * pageSize),
)
const hasNext = computed(() => filteredUsers.value.length > page.value * pageSize)
watch(query, () => {
  page.value = 1
})

async function refresh() {
  if (savingId.value !== null) return
  page.value = 1
  saveError.value = ''
  saved.value = ''
  await load()
}
async function save(user: User, request: () => Promise<User>) {
  if (busy.value) return
  savingId.value = user.id
  saveError.value = ''
  saved.value = ''
  try {
    const updated = await request()
    if (!active) return
    users.value = (users.value || []).map((item) => (item.id === updated.id ? updated : item))
    saved.value = 'Изменения для ' + updated.username + ' сохранены.'
  } catch (cause) {
    if (active)
      saveError.value = cause instanceof Error ? cause.message : 'Не удалось сохранить изменения'
  } finally {
    if (active) savingId.value = null
  }
}
function updateRole(user: User, event: Event) {
  const select = event.target as HTMLSelectElement
  const role = select.value as UserRole
  select.value = user.role
  if (role !== user.role && user.id !== auth.user?.id)
    void save(user, () => changeUserRole(user.id, role))
}
function updateDirector(user: User, event: Event) {
  const select = event.target as HTMLSelectElement
  const directorId = select.value ? Number(select.value) : null
  select.value = String(user.director_id ?? '')
  if (directorId !== (user.director_id ?? null) && user.role === 'researcher')
    void save(user, () => changeUserDirector(user.id, directorId))
}
onMounted(refresh)
onBeforeUnmount(() => {
  active = false
})
</script>
<template>
  <section class="panel" aria-labelledby="admin-users-title" :aria-busy="busy">
    <h2 id="admin-users-title">Пользователи</h2>
    <div class="admin-toolbar">
      <div class="form-field">
        <label for="user-search">Поиск пользователей</label
        ><input
          id="user-search"
          v-model="query"
          type="search"
          placeholder="Имя, email или организация"
        />
      </div>
      <button class="btn btn-secondary" :disabled="busy" @click="refresh">Обновить</button>
    </div>
    <p class="field-hint">
      Собственную роль администратора изменить нельзя. Директора можно назначить исследователю.
    </p>
    <p v-if="error || saveError" class="notice error" role="alert">{{ error || saveError }}</p>
    <p v-if="saved" class="notice" role="status">{{ saved }}</p>
    <p v-if="loading" role="status">Загрузка пользователей…</p>
    <template v-else-if="users">
      <p class="muted">Найдено пользователей: {{ filteredUsers.length }}</p>
      <div class="admin-table-wrap" role="region" aria-label="Список пользователей" tabindex="0">
        <table class="admin-table">
          <thead>
            <tr>
              <th scope="col">Пользователь</th>
              <th scope="col">Email</th>
              <th scope="col">Организация</th>
              <th scope="col">Роль</th>
              <th scope="col">Директор</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in visibleUsers" :key="user.id">
              <td>
                {{ user.username }}
                <span class="muted"
                  >#{{ user.id }}{{ user.id === auth.user?.id ? ' (вы)' : '' }}</span
                >
              </td>
              <td>{{ user.email }}</td>
              <td>{{ user.organization || '—' }}</td>
              <td>
                <select
                  :aria-label="'Роль: ' + user.username"
                  :value="user.role"
                  :disabled="busy || user.id === auth.user?.id"
                  @change="updateRole(user, $event)"
                >
                  <option value="researcher">Исследователь</option>
                  <option value="director">Директор</option>
                  <option value="admin">Администратор</option>
                </select>
              </td>
              <td>
                <select
                  :aria-label="'Директор: ' + user.username"
                  :value="user.director_id ?? ''"
                  :disabled="busy || user.role !== 'researcher'"
                  @change="updateDirector(user, $event)"
                >
                  <option value="">Не назначен</option>
                  <option
                    v-if="
                      user.director_id &&
                      !directors.some((director) => director.id === user.director_id)
                    "
                    :value="user.director_id"
                  >
                    #{{ user.director_id }} (роль изменена)
                  </option>
                  <option v-for="director in directors" :key="director.id" :value="director.id">
                    {{ director.username }} #{{ director.id }}
                  </option>
                </select>
              </td>
            </tr>
            <tr v-if="!visibleUsers.length">
              <td colspan="5" class="muted">Пользователи не найдены</td>
            </tr>
          </tbody>
        </table>
      </div>
      <AdminPagination :page="page" :has-next="hasNext" :loading="busy" @change="page = $event" />
    </template>
  </section>
</template>
