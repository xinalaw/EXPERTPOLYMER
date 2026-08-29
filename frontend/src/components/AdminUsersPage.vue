<script setup>
import { onMounted, ref } from 'vue'
import { changeUserRole, getUsers } from '@/api/users'

const props = defineProps({ currentUserId: { type: Number, default: null } })
const users = ref([])
const loading = ref(true)
const error = ref('')
const savingId = ref(null)

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    users.value = await getUsers()
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
}

async function updateRole(user, role) {
  if (role === user.role) return
  const previousRole = user.role
  savingId.value = user.id
  error.value = ''
  user.role = role
  try {
    const updated = await changeUserRole(user.id, role)
    Object.assign(user, updated)
  } catch (requestError) {
    user.role = previousRole
    error.value = requestError.message
  } finally {
    savingId.value = null
  }
}

onMounted(loadUsers)
</script>

<template>
  <main class="admin-page container">
    <div class="title-row">
      <div>
        <h1>Управление пользователями</h1>
        <p>Назначение ролей администратора, директора и исследователя.</p>
      </div>
      <button class="refresh" :disabled="loading" @click="loadUsers">Обновить</button>
    </div>

    <p v-if="error" class="message error">{{ error }}</p>
    <p v-if="loading" class="message">Загрузка пользователей…</p>

    <div v-else class="table-wrap">
      <table>
        <thead><tr><th>Пользователь</th><th>Email</th><th>Организация</th><th>Роль</th></tr></thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }} <small v-if="user.id === props.currentUserId">(вы)</small></td>
            <td>{{ user.email }}</td>
            <td>{{ user.organization || '—' }}</td>
            <td>
              <select
                :value="user.role"
                :disabled="savingId === user.id || user.id === props.currentUserId"
                @change="updateRole(user, $event.target.value)"
              >
                <option value="researcher">Исследователь</option>
                <option value="director">Директор</option>
                <option value="admin">Администратор</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<style scoped>
.admin-page { min-height: 65vh; padding-top: 3rem; padding-bottom: 3rem; }
.title-row { display: flex; justify-content: space-between; gap: 2rem; align-items: start; }
h1 { color: #1e3c72; font-size: 2.2rem; }
.refresh { border: 0; border-radius: 8px; padding: .7rem 1.2rem; color: white; background: #2a5298; cursor: pointer; }
.message { padding: 1rem; border-radius: 8px; background: #eef4ff; }
.error { color: #8a1c1c; background: #fff0f0; }
.table-wrap { overflow-x: auto; border: 1px solid #e1e7ef; border-radius: 12px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #e9edf2; }
th { color: #1e3c72; background: #f6f8fb; }
select { min-width: 155px; padding: .55rem; border: 1px solid #c8d2df; border-radius: 6px; background: white; }
small { color: #667; }
@media (max-width: 700px) { .title-row { display: block; } .refresh { margin-bottom: 1rem; } }
</style>
