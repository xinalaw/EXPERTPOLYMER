<template>
  <div v-if="isVisible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2>Регистрация</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-row">
          <div class="form-group">
            <label for="firstName">Имя</label>
            <input
              type="text"
              id="firstName"
              v-model="formData.firstName"
              required
              :class="{ error: errors.firstName }"
              placeholder="Введите имя"
            />
            <span v-if="errors.firstName" class="error-message">{{ errors.firstName }}</span>
          </div>

          <div class="form-group">
            <label for="lastName">Фамилия</label>
            <input
              type="text"
              id="lastName"
              v-model="formData.lastName"
              required
              :class="{ error: errors.lastName }"
              placeholder="Введите фамилию"
            />
            <span v-if="errors.lastName" class="error-message">{{ errors.lastName }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="formData.email"
            required
            :class="{ error: errors.email }"
            placeholder="Введите ваш email"
          />
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="organization">Организация</label>
          <input
            type="text"
            id="organization"
            v-model="formData.organization"
            :class="{ error: errors.organization }"
            placeholder="Название организации (необязательно)"
          />
          <span v-if="errors.organization" class="error-message">{{ errors.organization }}</span>
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <div class="password-input">
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="formData.password"
              required
              :class="{ error: errors.password }"
              placeholder="Создайте пароль"
            />
            <button
              type="button"
              class="password-toggle"
              @click="togglePassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          <div class="password-strength">
            <div class="strength-bar">
              <div 
                class="strength-fill" 
                :class="passwordStrength.class"
                :style="{ width: passwordStrength.width }"
              ></div>
            </div>
            <span class="strength-text">{{ passwordStrength.text }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Подтвердите пароль</label>
          <div class="password-input">
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              id="confirmPassword"
              v-model="formData.confirmPassword"
              required
              :class="{ error: errors.confirmPassword }"
              placeholder="Подтвердите пароль"
            />
            <button
              type="button"
              class="password-toggle"
              @click="toggleConfirmPassword"
            >
              {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.agreeTerms" required />
            <span class="checkmark"></span>
            Я согласен с <a href="#" class="terms-link">условиями использования</a> и <a href="#" class="terms-link">политикой конфиденциальности</a>
          </label>
          <span v-if="errors.agreeTerms" class="error-message">{{ errors.agreeTerms }}</span>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.newsletter" />
            <span class="checkmark"></span>
            Подписаться на новости и обновления системы
          </label>
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          {{ isLoading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>

        <div class="form-footer">
          <p>Уже есть аккаунт? <a href="#" @click.prevent="switchToLogin">Войти</a></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { registerUser, loginUser, mapUserToStorage } from '@/api/auth'

// Props
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'switch-to-login', 'register-success'])

// Reactive data
const formData = reactive({
  firstName: '',
  lastName: '',
  email: '',
  organization: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false,
  newsletter: false
})

const errors = reactive({
  firstName: '',
  lastName: '',
  email: '',
  organization: '',
  password: '',
  confirmPassword: '',
  agreeTerms: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isLoading = ref(false)

// Computed
const passwordStrength = computed(() => {
  const password = formData.password
  if (!password) return { width: '0%', class: '', text: '' }
  
  let score = 0
  let text = ''
  let className = ''
  
  if (password.length >= 8) score++
  if (/[a-z]/.test(password)) score++
  if (/[A-Z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^A-Za-z0-9]/.test(password)) score++
  
  switch (score) {
    case 0:
    case 1:
      text = 'Очень слабый'
      className = 'very-weak'
      break
    case 2:
      text = 'Слабый'
      className = 'weak'
      break
    case 3:
      text = 'Средний'
      className = 'medium'
      break
    case 4:
      text = 'Хороший'
      className = 'good'
      break
    case 5:
      text = 'Отличный'
      className = 'excellent'
      break
  }
  
  return {
    width: `${(score / 5) * 100}%`,
    class: className,
    text: text
  }
})

// Methods
const closeModal = () => {
  emit('close')
  resetForm()
}

const switchToLogin = () => {
  emit('switch-to-login')
  resetForm()
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => errors[key] = '')

  let isValid = true

  // First name validation
  if (!formData.firstName.trim()) {
    errors.firstName = 'Имя обязательно'
    isValid = false
  } else if (formData.firstName.trim().length < 2) {
    errors.firstName = 'Имя должно содержать минимум 2 символа'
    isValid = false
  }

  // Last name validation
  if (!formData.lastName.trim()) {
    errors.lastName = 'Фамилия обязательна'
    isValid = false
  } else if (formData.lastName.trim().length < 2) {
    errors.lastName = 'Фамилия должна содержать минимум 2 символа'
    isValid = false
  }

  // Email validation
  if (!formData.email) {
    errors.email = 'Email обязателен'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'Введите корректный email'
    isValid = false
  }

  // Password validation
  if (!formData.password) {
    errors.password = 'Пароль обязателен'
    isValid = false
  } else if (formData.password.length < 8) {
    errors.password = 'Пароль должен содержать минимум 8 символов'
    isValid = false
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
    errors.password = 'Пароль должен содержать заглавные и строчные буквы, а также цифры'
    isValid = false
  }

  // Confirm password validation
  if (!formData.confirmPassword) {
    errors.confirmPassword = 'Подтверждение пароля обязательно'
    isValid = false
  } else if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = 'Пароли не совпадают'
    isValid = false
  }

  // Terms agreement validation
  if (!formData.agreeTerms) {
    errors.agreeTerms = 'Необходимо согласиться с условиями использования'
    isValid = false
  }

  return isValid
}

const handleRegister = async () => {
  if (!validateForm()) return

  isLoading.value = true

  try {    
    await registerUser({
      first_name: formData.firstName,
      last_name: formData.lastName,
      email: formData.email,
      organization: formData.organization || null,
      password: formData.password,
      password_confirm: formData.confirmPassword,
    })

    const loginData = await loginUser(
      formData.email, 
      formData.password,
    )

    const userData = {
      ...mapUserToStorage(loginData.user, loginData.access_token),
      registerTime: new Date().toISOString(),
    }

    localStorage.setItem('user', JSON.stringify(userData))

    emit('register-success', userData)
    closeModal()
  } catch (error) {
    console.error('Ошибка регистрации:', error)
    errors.email = error.message || 'Ошибка подключения к серверу'
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  formData.firstName = ''
  formData.lastName = ''
  formData.email = ''
  formData.organization = ''
  formData.password = ''
  formData.confirmPassword = ''
  formData.agreeTerms = false
  formData.newsletter = false
  
  Object.keys(errors).forEach(key => errors[key] = '')
  
  showPassword.value = false
  showConfirmPassword.value = false
  isLoading.value = false
}

// Watch for modal visibility changes
watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    resetForm()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease-out;
}

.modal-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e3c72;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #1e3c72;
}

.register-form {
  padding: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8fafc;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.password-input {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #64748b;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-toggle:hover {
  color: #1e3c72;
}

.password-strength {
  margin-top: 0.5rem;
}

.strength-bar {
  width: 100%;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
}

.strength-fill.very-weak { background: #ef4444; }
.strength-fill.weak { background: #f97316; }
.strength-fill.medium { background: #eab308; }
.strength-fill.good { background: #22c55e; }
.strength-fill.excellent { background: #10b981; }

.strength-text {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.error-message {
  display: block;
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  font-size: 0.9rem;
  color: #64748b;
  line-height: 1.4;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  margin-right: 0.5rem;
  margin-top: 0.1rem;
  position: relative;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
  background: #667eea;
  border-color: #667eea;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.terms-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.terms-link:hover {
  color: #5a6fd8;
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

.form-footer {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.form-footer p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.form-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.form-footer a:hover {
  color: #5a6fd8;
  text-decoration: underline;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 480px) {
  .modal-container {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header,
  .register-form {
    padding: 1.5rem;
  }
  
  .modal-header h2 {
    font-size: 1.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

