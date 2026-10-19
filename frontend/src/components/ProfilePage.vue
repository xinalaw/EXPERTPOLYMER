<script setup lang="ts">
import { auth } from '@/stores/auth'
const roles: Record<string, string> = {
  researcher: 'Исследователь',
  director: 'Руководитель',
  admin: 'Администратор',
}
</script>
<template>
  <div class="page-shell">
    <header class="page-heading">
      <h1>Профиль</h1>
      <p>Данные вашей учётной записи.</p>
    </header>
    <section v-if="auth.user" class="panel">
      <h2>{{ auth.user.username }}</h2>
      <dl class="metrics">
        <div>
          <dt>Email</dt>
          <dd>{{ auth.user.email }}</dd>
        </div>
        <div>
          <dt>Организация</dt>
          <dd>{{ auth.user.organization || 'Не указана' }}</dd>
        </div>
        <div>
          <dt>Роль</dt>
          <dd>{{ roles[auth.user.role] || auth.user.role }}</dd>
        </div>
        <div>
          <dt>Номер учётной записи</dt>
          <dd>{{ auth.user.id }}</dd>
        </div>
      </dl>
      <p class="muted">Для изменения данных учётной записи обратитесь в поддержку.</p>
      <RouterLink to="/contacts" class="btn btn-secondary">Связаться с поддержкой</RouterLink>
    </section>
  </div>
</template>
