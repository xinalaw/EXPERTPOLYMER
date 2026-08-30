<script setup>
import { ref, onMounted } from 'vue'
import NavBar from './components/NavBar.vue';
import MainPage from './components/MainPage.vue';
import AnalysisPage from './components/AnalysisPage.vue';
import AnalysisHistoryPage from './components/AnalysisHistoryPage.vue';
import ContactsPage from './components/ContactsPage.vue';
import AboutPage from './components/AboutPage.vue';
import AdminPanelPage from './components/AdminPanelPage.vue';
import Footer from './components/Footer.vue';
import LoginModal from './components/LoginModal.vue';
import RegisterModal from './components/RegisterModal.vue';
import { getCurrentUser, getStoredUser, logoutUser } from '@/api/auth';

// Current page state
const currentPage = ref('home')

// Authentication state
const isAuthenticated = ref(false)
const user = ref(null)
const showLoginModal = ref(false)
const showRegisterModal = ref(false)

// Navigation
const navigateTo = (page) => {
  // Protect analysis pages
  if ((page === 'analysis' || page === 'history') && !isAuthenticated.value) {
    showLoginModal.value = true
    return
  }
  if (page === 'admin' && user.value?.role !== 'admin') return
  currentPage.value = page
}

// Authentication methods
const openLoginModal = () => {
  showLoginModal.value = true
  showRegisterModal.value = false
}

const openRegisterModal = () => {
  showRegisterModal.value = true
  showLoginModal.value = false
}

const closeAuthModals = () => {
  showLoginModal.value = false
  showRegisterModal.value = false
}

const switchToRegister = () => {
  showLoginModal.value = false
  showRegisterModal.value = true
}

const switchToLogin = () => {
  showRegisterModal.value = false
  showLoginModal.value = true
}

const handleLoginSuccess = (userData) => {
  isAuthenticated.value = true
  user.value = userData
  closeAuthModals()
  
  // Navigate to analysis page if user was trying to access it
  if (currentPage.value === 'home') {
    currentPage.value = 'analysis'
  }
}

const handleRegisterSuccess = (userData) => {
  isAuthenticated.value = true
  user.value = userData
  closeAuthModals()
  
  // Navigate to analysis page after successful registration
  currentPage.value = 'analysis'
}

const logout = () => {
  logoutUser()
  isAuthenticated.value = false
  user.value = null
  currentPage.value = 'home'
}

onMounted(async () => {
  const savedUser = getStoredUser()
  if (!savedUser?.token) return

  try {
    const profile = await getCurrentUser(savedUser.token)
    const userData = {
      ...savedUser,
      id: profile.id,
      email: profile.email,
      username: profile.username,
      role: profile.role,
      name: profile.username,
    }
    isAuthenticated.value = true
    user.value = userData

    const storage = localStorage.getItem('user') ? localStorage : sessionStorage
    storage.setItem('user', JSON.stringify(userData))
  } catch (error) {
    console.error('Session restore failed:', error)
    logoutUser()
  }
})
</script>

<template>
  <NavBar 
    :current-page="currentPage" 
    :is-authenticated="isAuthenticated"
    :user="user"
    @navigate="navigateTo"
    @open-login="openLoginModal"
    @open-register="openRegisterModal"
    @logout="logout"
  />
  <MainPage v-if="currentPage === 'home'" @navigate="navigateTo" />
  <AnalysisPage v-if="currentPage === 'analysis'" />
  <AnalysisHistoryPage v-if="currentPage === 'history'" />
  <AdminPanelPage
    v-if="currentPage === 'admin' && user?.role === 'admin'"
    :current-user-id="user?.id"
  />
  <AboutPage v-if="currentPage === 'about'" @navigate="navigateTo" />
  <ContactsPage v-if="currentPage === 'contacts'" />
  <Footer />
  
  <!-- Authentication Modals -->
  <LoginModal 
    :is-visible="showLoginModal"
    @close="closeAuthModals"
    @switch-to-register="switchToRegister"
    @login-success="handleLoginSuccess"
  />
  <RegisterModal 
    :is-visible="showRegisterModal"
    @close="closeAuthModals"
    @switch-to-login="switchToLogin"
    @register-success="handleRegisterSuccess"
  />
</template>

<style>
/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #ffffff;
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

/* Selection styles */
::selection {
  background: rgba(102, 126, 234, 0.2);
  color: #1e3c72;
}

::-moz-selection {
  background: rgba(102, 126, 234, 0.2);
  color: #1e3c72;
}

/* Focus styles for accessibility */
button:focus,
a:focus {
  outline: 2px solid #64b5f6;
  outline-offset: 2px;
}

/* Animation utilities */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Utility classes */
.fade-in {
  animation: fadeIn 0.6s ease-out;
}

.fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

/* Container utility */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Button base styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1rem;
}

h1 {
  font-size: 3rem;
}

h2 {
  font-size: 2.5rem;
}

h3 {
  font-size: 2rem;
}

h4 {
  font-size: 1.5rem;
}

p {
  margin-bottom: 1rem;
  line-height: 1.6;
}

/* Link styles */
a {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

a:hover {
  color: #5a6fd8;
}

/* Card styles */
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

/* Gradient text utility */
.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Loading animation */
.loading {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive utilities */
@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }
  
  h1 {
    font-size: 2.5rem;
  }
  
  h2 {
    font-size: 2rem;
  }
  
  h3 {
    font-size: 1.5rem;
  }
}

/* Print styles */
@media print {
  * {
    background: transparent !important;
    color: black !important;
    box-shadow: none !important;
    text-shadow: none !important;
  }
  
  a, a:visited {
    text-decoration: underline;
  }
  
  .navbar, .footer {
    display: none;
  }
}
</style>
