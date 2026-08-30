<script setup>
import { computed, onMounted, ref } from 'vue'
import { changeUserDirector, changeUserRole, getUsers } from '@/api/users'

const props = defineProps({ currentUserId: { type: Number, default: null } })
const users = ref([])
const loading = ref(true)
const error = ref('')
const savingId = ref(null)
const query = ref('')
const directors = computed(() => users.value.filter((user) => user.role === 'director'))
const filteredUsers = computed(() => {
  const needle = query.value.trim().toLocaleLowerCase('ru-RU')
  if (!needle) return users.value
  return users.value.filter((user) => `${user.username} ${user.email} ${user.organization || ''}`.toLocaleLowerCase('ru-RU').includes(needle))
})

async function loadUsers() {
  loading.value = true; error.value = ''
  try { users.value = await getUsers() } catch (requestError) { error.value = requestError.message } finally { loading.value = false }
}

async function save(user, request, rollback) {
  savingId.value = user.id; error.value = ''
  try { Object.assign(user, await request()) } catch (requestError) { rollback(); error.value = requestError.message } finally { savingId.value = null }
}

function updateRole(user, role) {
  if (role === user.role) return
  const previous = { role: user.role, director_id: user.director_id }
  user.role = role
  if (role !== 'researcher') user.director_id = null
  save(user, () => changeUserRole(user.id, role), () => Object.assign(user, previous))
}

function updateDirector(user, value) {
  const previous = user.director_id
  const directorId = value ? Number(value) : null
  user.director_id = directorId
  save(user, () => changeUserDirector(user.id, directorId), () => { user.director_id = previous })
}

onMounted(loadUsers)
</script>

<template>
  <section class="admin-content">
    <div class="admin-toolbar">
      <input v-model="query" class="admin-input" type="search" placeholder="Имя, email или организация">
      <button class="admin-button" :disabled="loading" @click="loadUsers">Обновить</button>
    </div>
    <p v-if="error" class="admin-message admin-error">{{ error }}</p>
    <p v-if="loading" class="admin-message">Загрузка пользователей…</p>
    <div v-else class="admin-table-wrap"><table class="admin-table">
      <thead><tr><th>Пользователь</th><th>Email</th><th>Организация</th><th>Роль</th><th>Директор</th></tr></thead>
      <tbody>
        <tr v-for="user in filteredUsers" :key="user.id">
          <td>{{ user.username }} <span v-if="user.id === props.currentUserId" class="admin-muted">(вы)</span></td>
          <td>{{ user.email }}</td><td>{{ user.organization || '—' }}</td>
          <td><select class="admin-input" :value="user.role" :disabled="savingId === user.id || user.id === props.currentUserId" @change="updateRole(user, $event.target.value)">
            <option value="researcher">Исследователь</option><option value="director">Директор</option><option value="admin">Администратор</option>
          </select></td>
          <td><select class="admin-input" :value="user.director_id ?? ''" :disabled="user.role !== 'researcher' || savingId === user.id" @change="updateDirector(user, $event.target.value)">
            <option value="">Не назначен</option><option v-for="director in directors" :key="director.id" :value="director.id">{{ director.username }}</option>
          </select></td>
        </tr>
        <tr v-if="!filteredUsers.length"><td colspan="5" class="admin-muted">Пользователи не найдены</td></tr>
      </tbody>
    </table></div>
  </section>
</template>
