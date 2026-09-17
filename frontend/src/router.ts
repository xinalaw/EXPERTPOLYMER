import { createRouter, createWebHashHistory } from 'vue-router'
import { auth, restoreSession } from '@/stores/auth'

export const router = createRouter({
  // Hash history also works when dist is hosted without server-side SPA rewrites.
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('./components/MainPage.vue'),
      meta: { title: 'Главная' },
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('./components/AboutPage.vue'),
      meta: { title: 'О системе' },
    },
    {
      path: '/contacts',
      name: 'contacts',
      component: () => import('./components/ContactsPage.vue'),
      meta: { title: 'Контакты' },
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: () => import('./components/AnalysisPage.vue'),
      meta: { title: 'Анализ', requiresAuth: true },
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('./components/AnalysisHistoryPage.vue'),
      meta: { title: 'История', requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('./components/ProfilePage.vue'),
      meta: { title: 'Профиль', requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('./components/SettingsPage.vue'),
      meta: { title: 'Настройки' },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('./components/AuthPage.vue'),
      props: { mode: 'login' },
      meta: { title: 'Вход' },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('./components/AuthPage.vue'),
      props: { mode: 'register' },
      meta: { title: 'Регистрация' },
    },
    {
      path: '/usage',
      name: 'usage',
      component: () => import('./components/UsagePage.vue'),
      meta: { title: 'Использование и данные' },
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('./components/NotFoundPage.vue'),
      meta: { title: 'Страница не найдена' },
    },
  ],
  scrollBehavior(to, from, saved) {
    if (to.path === from.path) return
    return saved || { top: 0 }
  },
})
router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    await restoreSession()
    if (!auth.user) return { name: 'login', query: { redirect: to.fullPath } }
  }
})
router.afterEach((to) => {
  document.title = to.meta.title + ' — Expert Polymer'
})

export function safeRedirect(value: unknown) {
  if (
    typeof value !== 'string' ||
    !value.startsWith('/') ||
    value.startsWith('//') ||
    value.includes('\\')
  )
    return '/analysis'
  const resolved = router.resolve(value)
  return resolved.name && !['login', 'register'].includes(String(resolved.name))
    ? resolved.fullPath
    : '/analysis'
}
