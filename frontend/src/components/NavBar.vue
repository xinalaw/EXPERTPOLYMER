<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { auth } from '@/stores/auth'
defineProps<{ loggingOut: boolean }>()
const emit = defineEmits<{ logout: [] }>()
const route = useRoute()
const mobileOpen = ref(false)
const userOpen = ref(false)
const userMenu = ref<HTMLElement | null>(null)
const userButton = ref<HTMLButtonElement | null>(null)
const mobileButton = ref<HTMLButtonElement | null>(null)
const links = computed(() => [
  { name: 'home', label: 'Главная' },
  { name: 'analysis', label: 'Анализ' },
  { name: 'generation', label: 'Генерация' },
  ...(auth.user ? [{ name: 'history', label: 'История' }] : []),
  ...(auth.user?.role === 'admin' ? [{ name: 'admin', label: 'Админ-панель' }] : []),
  { name: 'about', label: 'О системе' },
  { name: 'contacts', label: 'Контакты' },
])
watch(
  () => route.fullPath,
  () => {
    mobileOpen.value = false
    userOpen.value = false
  },
)
watch(
  () => auth.user?.id,
  () => {
    userOpen.value = false
  },
)
function outside(event: PointerEvent) {
  if (!userMenu.value?.contains(event.target as Node)) userOpen.value = false
}
function escape() {
  if (userOpen.value) {
    userOpen.value = false
    userButton.value?.focus()
  } else if (mobileOpen.value) {
    mobileOpen.value = false
    mobileButton.value?.focus()
  }
}
onMounted(() => document.addEventListener('pointerdown', outside))
onBeforeUnmount(() => document.removeEventListener('pointerdown', outside))
</script>
<template>
  <header class="navbar" @keydown.esc="escape">
    <nav class="nav-container" aria-label="Основная навигация">
      <RouterLink to="/" class="brand">GranulAI<span>AI Analysis System</span></RouterLink>
      <button
        ref="mobileButton"
        class="menu-toggle"
        :aria-expanded="mobileOpen"
        aria-controls="site-navigation"
        @click="mobileOpen = !mobileOpen"
      >
        {{ mobileOpen ? 'Закрыть меню' : 'Меню' }}
      </button>
      <div id="site-navigation" class="nav-content" :class="{ 'is-open': mobileOpen }">
        <ul class="nav-links">
          <li v-for="link in links" :key="link.name">
            <RouterLink :to="{ name: link.name }">{{ link.label }}</RouterLink>
          </li>
        </ul>
        <div v-if="auth.user" ref="userMenu" class="user-menu">
          <button
            ref="userButton"
            class="user-button"
            :aria-expanded="userOpen"
            aria-controls="user-navigation"
            @click="userOpen = !userOpen"
          >
            <span class="user-name">{{ auth.user.username }}</span>
            <svg
              class="user-chevron"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
              focusable="false"
            >
              <path d="m6 9 6 6 6-6" />
            </svg>
          </button>
          <ul v-if="userOpen" id="user-navigation" class="user-dropdown">
            <li><RouterLink to="/profile">Профиль</RouterLink></li>
            <li><RouterLink to="/settings">Настройки</RouterLink></li>
            <li>
              <button :disabled="loggingOut" @click="emit('logout')">
                {{ loggingOut ? 'Выход…' : 'Выйти' }}
              </button>
            </li>
          </ul>
        </div>
        <div v-else class="guest-actions">
          <RouterLink
            :to="{
              name: 'login',
              query: { redirect: route.fullPath === '/' ? '/analysis' : route.fullPath },
            }"
            >Войти</RouterLink
          ><RouterLink class="register-link" to="/register">Регистрация</RouterLink>
        </div>
      </div>
    </nav>
  </header>
</template>
<style scoped>
.navbar {
  background: var(--nav-gradient);
  color: white;
  position: sticky;
  top: 0;
  z-index: 30;
  box-shadow: var(--shadow);
}
.nav-container {
  max-width: 1320px;
  margin: auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}
.brand {
  font-size: 1.5rem;
  font-weight: 750;
  flex-shrink: 0;
  line-height: 1.2;
}
.brand span {
  display: block;
  font-size: 0.75rem;
  font-weight: 400;
  color: #d2e3fb;
  margin-top: 0.3rem;
}
a,
a:hover {
  color: white;
  text-decoration: none;
}
.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  width: 100%;
  min-width: 0;
}
.user-name {
  min-width: 0;
}
.user-chevron {
  display: block;
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  transform: translateY(2px);
}
.nav-links,
.user-dropdown {
  list-style: none;
  margin: 0;
  padding: 0;
}
.nav-links {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.nav-links a {
  display: block;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
}
.nav-links a.router-link-exact-active,
.nav-links a:hover {
  border-bottom-color: #c4dfff;
}
.guest-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.register-link {
  background: #a92f3c;
  padding: 0.65rem 1rem;
  border-radius: var(--radius);
}
.user-menu {
  position: relative;
  min-width: 0;
}
.user-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 220px;
  overflow-wrap: anywhere;
  color: white;
  background: #ffffff1a;
  border: 1px solid #ffffff66;
  border-radius: var(--radius);
  padding: 0.65rem 1rem;
  text-align: left;
}
.user-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 0.5rem);
  width: 210px;
  background: white;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.5rem;
}
.user-dropdown a,
.user-dropdown a:hover,
.user-dropdown button {
  color: var(--text);
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.75rem;
  border: 0;
  background: white;
  border-radius: 0.4rem;
}
.user-dropdown a:hover,
.user-dropdown button:hover {
  background: var(--surface-muted);
}
.menu-toggle {
  display: none;
  color: white;
  background: transparent;
  border: 1px solid #ffffff99;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
}
@media (max-width: 1100px) {
  .nav-container {
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.8rem 1rem;
  }
  .menu-toggle {
    display: block;
  }
  .nav-content {
    display: none;
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
    max-height: 70dvh;
    overflow-y: auto;
  }
  .nav-content.is-open {
    display: flex;
  }
  .nav-links {
    align-items: stretch;
    flex-direction: column;
    gap: 0.2rem;
  }
  .nav-links a {
    padding: 0.5rem;
  }
  .user-button {
    max-width: 100%;
  }
  .user-dropdown {
    position: static;
    margin-top: 0.5rem;
    width: 100%;
  }
}
</style>
