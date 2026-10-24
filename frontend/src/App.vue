<script setup lang="ts">
import { nextTick, onBeforeUnmount, onErrorCaptured, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PrototypeNotice from './components/PrototypeNotice.vue'
import NavBar from './components/NavBar.vue'
import Footer from './components/Footer.vue'
import { auth, restoreSession, signOut } from '@/stores/auth'
import { SESSION_KEY } from '@/api/auth'
import { resetAnalysis, useAnalysis } from '@/composables/useAnalysis'
import '@/stores/preferences'

const route = useRoute()
const router = useRouter()
const loggingOut = ref(false)
const logoutError = ref('')
const renderError = ref(false)
const { phase, file } = useAnalysis()
onErrorCaptured(() => {
  renderError.value = true
  return false
})
const stopErrorHandler = router.onError(() => {
  renderError.value = true
})
watch(
  () => auth.user?.id,
  (id, previous) => {
    if (previous !== id) resetAnalysis()
  },
)
watch(
  [
    () => auth.ready,
    () => auth.user,
    () => route.meta.requiresAuth,
    () => route.meta.requiresAdmin,
  ],
  () => {
    if (auth.ready && !auth.user && route.meta.requiresAuth)
      router.replace({ name: 'login', query: { redirect: route.fullPath } })
    else if (auth.ready && auth.user && route.meta.requiresAdmin && auth.user.role !== 'admin')
      router.replace({ name: 'profile' })
  },
)
watch(
  () => route.path,
  async () => {
    renderError.value = false
    await nextTick()
    const heading = document.querySelector<HTMLElement>('main h1')
    heading?.setAttribute('tabindex', '-1')
    heading?.focus({ preventScroll: true })
  },
)
async function logout() {
  if (loggingOut.value) return
  loggingOut.value = true
  logoutError.value = ''
  try {
    await signOut()
    await router.replace('/')
  } catch (cause) {
    logoutError.value =
      cause instanceof Error ? cause.message : 'Не удалось выйти. Повторите попытку.'
  } finally {
    loggingOut.value = false
  }
}
function retry() {
  window.location.reload()
}
function refreshSession() {
  if (document.visibilityState === 'visible') void restoreSession(true)
}
function syncSession(event: StorageEvent) {
  if (event.key === SESSION_KEY || event.key === null) void restoreSession(true)
}
function beforeUnload(event: BeforeUnloadEvent) {
  if (phase.value === 'running' || (file.value && phase.value !== 'complete')) {
    event.preventDefault()
    event.returnValue = ''
  }
}
onMounted(() => {
  void restoreSession()
  window.addEventListener('focus', refreshSession)
  window.addEventListener('storage', syncSession)
  window.addEventListener('beforeunload', beforeUnload)
})
onBeforeUnmount(() => {
  stopErrorHandler()
  window.removeEventListener('focus', refreshSession)
  window.removeEventListener('storage', syncSession)
  window.removeEventListener('beforeunload', beforeUnload)
})
</script>
<template>
  <a class="skip-link" href="#main-content" @click.prevent="($refs.main as HTMLElement)?.focus()"
    >Перейти к содержимому</a
  >
  <NavBar :logging-out="loggingOut" @logout="logout" />
  <main id="main-content" ref="main" tabindex="-1">
    <PrototypeNotice />
    <div v-if="auth.error" class="page-shell notice error" role="alert">
      <p>{{ auth.error }}</p>
      <button class="btn btn-secondary" @click="restoreSession(true)">Проверить соединение</button>
    </div>
    <p v-if="auth.expired" class="page-shell notice" role="status">
      Сессия завершилась. Войдите снова, чтобы продолжить.
    </p>
    <p v-if="logoutError" class="page-shell notice error" role="alert">{{ logoutError }}</p>
    <section v-if="renderError" class="page-shell panel">
      <h1>Не удалось открыть страницу</h1>
      <p>Попробуйте обновить страницу.</p>
      <button class="btn btn-primary" @click="retry">Обновить страницу</button>
    </section>
    <p v-else-if="route.meta.requiresAuth && !auth.ready" class="page-shell panel" role="status">
      Проверка сессии…
    </p>
    <RouterView
      v-else-if="!route.meta.requiresAdmin || auth.user?.role === 'admin'"
      :key="route.path + ':' + (route.meta.requiresAuth ? (auth.user?.id ?? 'guest') : '')"
    />
  </main>
  <Footer />
</template>
