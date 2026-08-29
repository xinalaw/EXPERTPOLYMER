<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-logo" @click="navigateTo('home')" style="cursor: pointer;">
        <h2>Expert Polymer</h2>
        <span class="nav-subtitle">AI Analysis System</span>
      </div>
      
      <ul class="nav-menu">
        <li class="nav-item">
          <a href="#" @click.prevent="navigateTo('home')" 
             class="nav-link" 
             :class="{ active: currentPage === 'home' }">Главная</a>
        </li>
        <li class="nav-item">
          <a href="#" @click.prevent="navigateTo('analysis')" 
             class="nav-link" 
             :class="{ active: currentPage === 'analysis' }">Анализ</a>
        </li>
        <li class="nav-item" v-if="isAuthenticated">
          <a href="#" @click.prevent="navigateTo('history')" 
             class="nav-link" 
             :class="{ active: currentPage === 'history' }">История</a>
        </li>
        <li class="nav-item">
          <a href="#" @click.prevent="navigateTo('about')" 
             class="nav-link" 
             :class="{ active: currentPage === 'about' }">О системе</a>
        </li>
        <li class="nav-item">
          <a href="#" @click.prevent="navigateTo('contacts')" 
             class="nav-link" 
             :class="{ active: currentPage === 'contacts' }">Контакты</a>
        </li>
      </ul>
      
      <div class="nav-actions">
        <!-- Authenticated User Menu -->
        <div v-if="isAuthenticated" class="user-menu">
          <div class="user-info" @click="toggleDropdown">
            <div class="user-avatar">
              {{ userInitials }}
            </div>
            <div class="user-details">
              <span class="user-name">{{ user?.name || user?.email }}</span>
              <span class="user-email">{{ user?.email }}</span>
            </div>
            <div class="dropdown-arrow" :class="{ active: showDropdown }">▼</div>
          </div>
          
          <div v-if="showDropdown" class="user-dropdown">
            <a href="#" @click.prevent="navigateTo('analysis')" class="dropdown-item">
              <span class="dropdown-icon">🔬</span>
              Анализ
            </a>
            <a href="#" @click.prevent="navigateTo('history')" class="dropdown-item">
              <span class="dropdown-icon">📊</span>
              История
            </a>
            <a v-if="user?.role === 'admin'" href="#" @click.prevent="navigateTo('admin-users')" class="dropdown-item">
              <span class="dropdown-icon">🛡️</span>
              Пользователи
            </a>
            <a href="#" @click.prevent="navigateTo('profile')" class="dropdown-item">
              <span class="dropdown-icon">👤</span>
              Профиль
            </a>
            <a href="#" @click.prevent="navigateTo('settings')" class="dropdown-item">
              <span class="dropdown-icon">⚙️</span>
              Настройки
            </a>
            <div class="dropdown-divider"></div>
            <a href="#" @click.prevent="logout" class="dropdown-item logout">
              <span class="dropdown-icon">🚪</span>
              Выйти
            </a>
          </div>
        </div>
        
        <!-- Guest Actions -->
        <div v-else class="guest-actions">
          <button class="btn-secondary" @click="openLoginModal">Войти</button>
          <button class="btn-primary" @click="openRegisterModal">Регистрация</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  currentPage: {
    type: String,
    default: 'home'
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['navigate', 'open-login', 'open-register', 'logout'])

// State
const showDropdown = ref(false)

// Computed
const userInitials = computed(() => {
  if (!props.user) return ''
  const name = props.user.name || props.user.email || ''
  return name.split(' ').map(word => word.charAt(0)).join('').toUpperCase().slice(0, 2)
})

// Methods
const navigateTo = (page) => {
  emit('navigate', page)
}

const openLoginModal = () => {
  emit('open-login')
}

const openRegisterModal = () => {
  emit('open-register')
}

const logout = () => {
  emit('logout')
}

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const handleClickOutside = (event) => {
  if (!event.target.closest('.user-menu')) {
    showDropdown.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

.nav-logo h2 {
  color: #ffffff;
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.nav-subtitle {
  color: #a8c8ec;
  font-size: 0.85rem;
  font-weight: 400;
  display: block;
  margin-top: -2px;
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 2rem;
}

.nav-item {
  position: relative;
}

.nav-link {
  color: #ffffff;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  padding: 0.5rem 0;
  transition: all 0.3s ease;
  position: relative;
}

.nav-link:hover {
  color: #64b5f6;
  transform: translateY(-1px);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #64b5f6, #42a5f5);
  transition: width 0.3s ease;
}

.nav-link:hover::after {
  width: 100%;
}

.nav-link.active {
  color: #64b5f6;
}

.nav-link.active::after {
  width: 100%;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
  background: linear-gradient(135deg, #ff5252 0%, #e53935 100%);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-right: 1rem;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.6);
}

/* User Menu Styles */
.user-menu {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.2);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-name {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  line-height: 1.2;
}

.user-email {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  line-height: 1.2;
}

.dropdown-arrow {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  transition: transform 0.3s ease;
}

.dropdown-arrow.active {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  min-width: 200px;
  overflow: hidden;
  z-index: 1000;
  animation: dropdownSlide 0.3s ease-out;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  color: #374151;
  text-decoration: none;
  transition: all 0.3s ease;
  border-bottom: 1px solid #f3f4f6;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #f8fafc;
  color: #1e3c72;
}

.dropdown-item.logout:hover {
  background: #fef2f2;
  color: #dc2626;
}

.dropdown-icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 0.5rem 0;
}

.guest-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
