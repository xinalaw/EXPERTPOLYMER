<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { registerUser } from '@/api/auth'
import { auth, signIn } from '@/stores/auth'
import { safeRedirect } from '@/router'
import FormField from './ui/FormField.vue'

const props = defineProps<{ mode: 'login' | 'register' }>()
const route = useRoute()
const router = useRouter()
const registering = computed(() => props.mode === 'register')
const title = computed(() => (registering.value ? 'Создать учётную запись' : 'Войти в систему'))
const form = reactive({
  first_name: '',
  last_name: '',
  organization: '',
  email: '',
  password: '',
  password_confirm: '',
  remember: false,
})
const errors = reactive<Record<string, string>>({})
const error = ref('')
const errorSummary = ref<HTMLElement | null>(null)
const busy = ref(false)
const showPassword = ref(false)
const registered = ref(false)
let alive = true
onBeforeUnmount(() => {
  alive = false
  form.password = ''
  form.password_confirm = ''
})
onBeforeRouteLeave(() => !busy.value)
watch(
  () => props.mode,
  () => {
    form.password = ''
    form.password_confirm = ''
    error.value = ''
    registered.value = false
    Object.keys(errors).forEach((key) => delete errors[key])
  },
)
async function submit() {
  if (busy.value) return
  error.value = ''
  Object.keys(errors).forEach((key) => delete errors[key])
  form.email = form.email.trim()
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.email = 'Введите корректный email.'
  if (form.password.length < 8 || new TextEncoder().encode(form.password).length > 72)
    errors.password = 'Пароль: от 8 символов до 72 байт.'
  if (registering.value && !registered.value) {
    form.first_name = form.first_name.trim()
    form.last_name = form.last_name.trim()
    if (form.first_name.length < 2) errors.first_name = 'Имя должно содержать минимум 2 символа.'
    if (form.last_name.length < 2) errors.last_name = 'Фамилия должна содержать минимум 2 символа.'
    if (form.password !== form.password_confirm) errors.password_confirm = 'Пароли не совпадают.'
  }
  if (Object.keys(errors).length) {
    error.value = 'Проверьте отмеченные поля.'
    await nextTick()
    errorSummary.value?.focus()
    return
  }
  busy.value = true
  try {
    if (registering.value && !registered.value) {
      await registerUser({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        organization: form.organization.trim() || null,
        password: form.password,
        password_confirm: form.password_confirm,
      })
      registered.value = true
    }
    await signIn(form.email, form.password, form.remember)
    if (!alive) return
    form.password = ''
    form.password_confirm = ''
    busy.value = false
    await router.replace(safeRedirect(route.query.redirect))
  } catch (cause) {
    if (!alive) return
    error.value =
      (registered.value ? 'Учётная запись создана, но вход не завершён. Повторите вход. ' : '') +
      (cause instanceof Error ? cause.message : 'Не удалось выполнить запрос.')
    await nextTick()
    errorSummary.value?.focus()
  } finally {
    busy.value = false
  }
}
</script>
<template>
  <div class="page-shell narrow">
    <header class="page-heading">
      <h1>{{ title }}</h1>
      <p>
        {{
          registering
            ? 'Для анализа изображений и сохранения результатов.'
            : 'Продолжите работу с вашими исследованиями.'
        }}
      </p>
    </header>
    <section v-if="auth.user" class="panel">
      <p>Вы вошли как {{ auth.user.username }}.</p>
      <RouterLink class="btn btn-primary" :to="safeRedirect(route.query.redirect)"
        >Продолжить</RouterLink
      >
    </section>
    <form v-else class="panel form-stack" novalidate :aria-busy="busy" @submit.prevent="submit">
      <p v-if="error" ref="errorSummary" class="notice error" role="alert" tabindex="-1">
        {{ error }}
      </p>
      <template v-if="registering && !registered">
        <FormField
          v-model="form.first_name"
          label="Имя"
          autocomplete="given-name"
          required
          maxlength="50"
          :disabled="busy"
          :error="errors.first_name"
        />
        <FormField
          v-model="form.last_name"
          label="Фамилия"
          autocomplete="family-name"
          required
          maxlength="50"
          :disabled="busy"
          :error="errors.last_name"
        />
        <FormField
          v-model="form.organization"
          label="Организация (необязательно)"
          autocomplete="organization"
          maxlength="100"
          :disabled="busy"
        />
      </template>
      <FormField
        v-model="form.email"
        label="Email"
        type="email"
        autocomplete="username"
        required
        maxlength="254"
        :disabled="busy || registered"
        :error="errors.email"
      />
      <FormField
        v-model="form.password"
        label="Пароль"
        :type="showPassword ? 'text' : 'password'"
        :autocomplete="registering && !registered ? 'new-password' : 'current-password'"
        required
        :disabled="busy"
        :error="errors.password"
        :hint="registering ? 'Минимум 8 символов. Используйте уникальный пароль.' : undefined"
      />
      <FormField
        v-if="registering && !registered"
        v-model="form.password_confirm"
        label="Подтвердите пароль"
        :type="showPassword ? 'text' : 'password'"
        autocomplete="new-password"
        required
        :disabled="busy"
        :error="errors.password_confirm"
      />
      <button
        class="text-button"
        type="button"
        :aria-pressed="showPassword"
        @click="showPassword = !showPassword"
      >
        {{ showPassword ? 'Скрыть пароль' : 'Показать пароль' }}
      </button>
      <label class="checkbox-row"
        ><input v-model="form.remember" type="checkbox" :disabled="busy" /> Запомнить меня на этом
        устройстве</label
      >
      <p class="muted">
        Сведения о хранении данных: <RouterLink to="/usage">использование системы</RouterLink>.
      </p>
      <button class="btn btn-primary" type="submit" :disabled="busy">
        {{ busy ? 'Подождите…' : registering && !registered ? 'Зарегистрироваться' : 'Войти' }}
      </button>
      <p>
        <RouterLink :to="{ name: registering ? 'login' : 'register', query: route.query }">{{
          registering ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Зарегистрироваться'
        }}</RouterLink>
      </p>
      <RouterLink to="/">Вернуться на главную</RouterLink>
    </form>
  </div>
</template>
