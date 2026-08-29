<template>
  <div class="contacts-page">
    <!-- Header Section -->
    <section class="contacts-header">
      <div class="container">
        <div class="header-content">
          <h1 class="page-title">Контакты</h1>
          <p class="page-description">
            Свяжитесь с нами для получения консультации по анализу композитных материалов 
            или для обсуждения возможностей сотрудничества
          </p>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <section class="contacts-main">
      <div class="container">
        <div class="contacts-grid">
          <!-- Contact Information -->
          <div class="contact-info-section">
            <h2>Наши контакты</h2>
            
            <div class="contact-cards">
              <div class="contact-card">
                <div class="contact-icon">
                  <div class="icon-location"></div>
                </div>
                <div class="contact-details">
                  <h3>Адрес</h3>
                  <p>Казань, Россия</p>
                  <p>ул. Петербургская 52, ИТ-Парк</p>
                </div>
              </div>

              <div class="contact-card">
                <div class="contact-icon">
                  <div class="icon-phone"></div>
                </div>
                <div class="contact-details">
                  <h3>Телефон</h3>
                  <p>+7 (937) 368-96-93</p>
                  <p>Пн-Пт: 9:00 - 18:00</p>
                </div>
              </div>

              <div class="contact-card">
                <div class="contact-icon">
                  <div class="icon-email"></div>
                </div>
                <div class="contact-details">
                  <h3>Email</h3>
                  <p>info@expertpolymer.ru</p>
                  <p>support@expertpolymer.ru</p>
                </div>
              </div>

              <div class="contact-card">
                <div class="contact-icon">
                  <div class="icon-time"></div>
                </div>
                <div class="contact-details">
                  <h3>Время работы</h3>
                  <p>Понедельник - Пятница: 9:00 - 18:00</p>
                  <p>Суббота - Воскресенье: Выходной</p>
                </div>
              </div>
            </div>

            <!-- Social Links -->
            <div class="social-section">
              <h3>Мы в социальных сетях</h3>
              <div class="social-links">
                <a href="#" class="social-link" title="GitHub">
                  <div class="icon-github"></div>
                  <span>GitHub</span>
                </a>
                <a href="#" class="social-link" title="LinkedIn">
                  <div class="icon-linkedin"></div>
                  <span>LinkedIn</span>
                </a>
                <a href="#" class="social-link" title="Telegram">
                  <div class="icon-telegram"></div>
                  <span>Telegram</span>
                </a>
                <a href="#" class="social-link" title="ResearchGate">
                  <div class="icon-research"></div>
                  <span>ResearchGate</span>
                </a>
              </div>
            </div>
          </div>

          <!-- Contact Form -->
          <div class="contact-form-section">
            <h2>Написать нам</h2>
            <form @submit.prevent="handleSubmit" class="contact-form">
              <div class="form-row">
                <div class="form-group">
                  <label for="firstName">Имя *</label>
                  <input 
                    type="text" 
                    id="firstName" 
                    v-model="formData.firstName" 
                    required
                    placeholder="Введите ваше имя"
                    :class="{ error: errors.firstName }"
                  />
                  <span v-if="errors.firstName" class="error-message">{{ errors.firstName }}</span>
                </div>
                
                <div class="form-group">
                  <label for="lastName">Фамилия *</label>
                  <input 
                    type="text" 
                    id="lastName" 
                    v-model="formData.lastName" 
                    required
                    placeholder="Введите вашу фамилию"
                    :class="{ error: errors.lastName }"
                  />
                  <span v-if="errors.lastName" class="error-message">{{ errors.lastName }}</span>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="email">Email *</label>
                  <input 
                    type="email" 
                    id="email" 
                    v-model="formData.email" 
                    required
                    placeholder="your@email.com"
                    :class="{ error: errors.email }"
                  />
                  <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
                </div>
                
                <div class="form-group">
                  <label for="phone">Телефон</label>
                  <input 
                    type="tel" 
                    id="phone" 
                    v-model="formData.phone" 
                    placeholder="+7 (999) 123-45-67"
                    :class="{ error: errors.phone }"
                  />
                  <span v-if="errors.phone" class="error-message">{{ errors.phone }}</span>
                </div>
              </div>

              <div class="form-group">
                <label for="organization">Организация</label>
                <input 
                  type="text" 
                  id="organization" 
                  v-model="formData.organization" 
                  placeholder="Название организации"
                />
              </div>

              <div class="form-group">
                <label for="subject">Тема обращения *</label>
                <select 
                  id="subject" 
                  v-model="formData.subject" 
                  required
                  :class="{ error: errors.subject }"
                >
                  <option value="">Выберите тему</option>
                  <option value="consultation">Консультация по анализу</option>
                  <option value="cooperation">Сотрудничество</option>
                  <option value="technical-support">Техническая поддержка</option>
                  <option value="feedback">Отзыв о системе</option>
                  <option value="other">Другое</option>
                </select>
                <span v-if="errors.subject" class="error-message">{{ errors.subject }}</span>
              </div>

              <div class="form-group">
                <label for="message">Сообщение *</label>
                <textarea 
                  id="message" 
                  v-model="formData.message" 
                  required
                  rows="6"
                  placeholder="Опишите ваш вопрос или предложение..."
                  :class="{ error: errors.message }"
                ></textarea>
                <span v-if="errors.message" class="error-message">{{ errors.message }}</span>
              </div>

              <div class="form-options">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="formData.agreePrivacy" required>
                  <span class="checkmark"></span>
                  Я согласен с <a href="#" class="privacy-link">политикой конфиденциальности</a>
                </label>
              </div>

              <div class="form-options">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="formData.newsletter">
                  <span class="checkmark"></span>
                  Подписаться на новости и обновления
                </label>
              </div>

              <button type="submit" class="btn-submit" :disabled="isSubmitting">
                <span v-if="!isSubmitting">Отправить сообщение</span>
                <span v-else class="loading-container">
                  <div class="loading"></div>
                  Отправка...
                </span>
              </button>

              <div v-if="submitStatus" class="submit-status" :class="submitStatus.type">
                {{ submitStatus.message }}
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>

    <!-- Map Section -->
    <section class="map-section">
      <div class="container">
        <h2>Как нас найти</h2>
        <div class="map-container">
          <div class="map-placeholder">
            <div class="map-icon">
              <div class="icon-map"></div>
            </div>
            <h3>ИТ-Парк, Казань</h3>
            <p>ул. Петербургская 52</p>
            <div class="map-actions">
              <button class="btn-map" @click="openInMaps">Открыть в картах</button>
              <button class="btn-map secondary" @click="getDirections">Проложить маршрут</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// Form data
const formData = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  organization: '',
  subject: '',
  message: '',
  agreePrivacy: false,
  newsletter: false
})

// State
const isSubmitting = ref(false)
const errors = reactive({})
const submitStatus = ref(null)

// Methods
const validateForm = () => {
  errors.firstName = ''
  errors.lastName = ''
  errors.email = ''
  errors.phone = ''
  errors.subject = ''
  errors.message = ''
  
  if (!formData.firstName.trim()) {
    errors.firstName = 'Имя обязательно'
    return false
  }
  
  if (!formData.lastName.trim()) {
    errors.lastName = 'Фамилия обязательна'
    return false
  }
  
  if (!formData.email) {
    errors.email = 'Email обязателен'
    return false
  }
  
  if (!/\S+@\S+\.\S+/.test(formData.email)) {
    errors.email = 'Введите корректный email'
    return false
  }
  
  if (formData.phone && !/^[\+]?[0-9\s\-\(\)]{10,}$/.test(formData.phone)) {
    errors.phone = 'Введите корректный номер телефона'
    return false
  }
  
  if (!formData.subject) {
    errors.subject = 'Выберите тему обращения'
    return false
  }
  
  if (!formData.message.trim()) {
    errors.message = 'Сообщение обязательно'
    return false
  }
  
  if (formData.message.trim().length < 10) {
    errors.message = 'Сообщение должно содержать минимум 10 символов'
    return false
  }
  
  if (!formData.agreePrivacy) {
    submitStatus.value = {
      type: 'error',
      message: 'Необходимо согласиться с политикой конфиденциальности'
    }
    return false
  }
  
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isSubmitting.value = true
  submitStatus.value = null
  
  try {
    // Здесь будет API вызов для отправки сообщения
    // const response = await contactAPI.sendMessage(formData)
    
    // Симуляция API вызова
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    submitStatus.value = {
      type: 'success',
      message: 'Сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.'
    }
    
    // Очистка формы
    Object.keys(formData).forEach(key => {
      if (typeof formData[key] === 'boolean') {
        formData[key] = false
      } else {
        formData[key] = ''
      }
    })
    
  } catch (error) {
    console.error('Submit error:', error)
    submitStatus.value = {
      type: 'error',
      message: 'Произошла ошибка при отправке сообщения. Попробуйте еще раз.'
    }
  } finally {
    isSubmitting.value = false
  }
}

const openInMaps = () => {
  const address = encodeURIComponent('ул. Петербургская 52, Казань')
  window.open(`https://yandex.ru/maps/?text=${address}`, '_blank')
}

const getDirections = () => {
  const address = encodeURIComponent('ул. Петербургская 52, Казань')
  window.open(`https://yandex.ru/maps/?text=${address}&rtext=~${address}`, '_blank')
}
</script>

<style scoped>
.contacts-page {
  min-height: 100vh;
  background: #f8fafc;
}

/* Header Section */
.contacts-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 4rem 0;
  color: white;
  text-align: center;
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  letter-spacing: -1px;
}

.page-description {
  font-size: 1.2rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Main Content */
.contacts-main {
  padding: 4rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.contacts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
}

/* Contact Information */
.contact-info-section h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e3c72;
  margin-bottom: 2rem;
}

.contact-cards {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.contact-card {
  background: white;
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  transition: all 0.3s ease;
}

.contact-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.contact-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.contact-details h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e3c72;
  margin-bottom: 0.5rem;
}

.contact-details p {
  color: #64748b;
  margin-bottom: 0.25rem;
  line-height: 1.5;
}

/* Social Section */
.social-section h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e3c72;
  margin-bottom: 1.5rem;
}

.social-links {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.social-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: white;
  border-radius: 10px;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.social-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  color: #1e3c72;
}

/* Contact Form */
.contact-form-section {
  background: white;
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.contact-form-section h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e3c72;
  margin-bottom: 2rem;
}

.contact-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #374151;
  font-size: 0.95rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.875rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8fafc;
  font-family: inherit;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.error-message {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.form-options {
  margin-bottom: 0.5rem;
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
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
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
  font-size: 0.8rem;
  font-weight: bold;
}

.privacy-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.privacy-link:hover {
  color: #5a6fd8;
}

.btn-submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  margin-top: 1rem;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-status {
  padding: 1rem;
  border-radius: 10px;
  font-weight: 500;
  margin-top: 1rem;
}

.submit-status.success {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  color: #0369a1;
}

.submit-status.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

/* Map Section */
.map-section {
  padding: 4rem 0;
  background: white;
}

.map-section h2 {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e3c72;
  margin-bottom: 3rem;
}

.map-container {
  max-width: 800px;
  margin: 0 auto;
}

.map-placeholder {
  background: #f8fafc;
  border: 2px dashed #cbd5e1;
  border-radius: 15px;
  padding: 3rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.map-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
}

.map-placeholder h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e3c72;
  margin: 0;
}

.map-placeholder p {
  color: #64748b;
  margin: 0;
}

.map-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-map {
  padding: 0.75rem 1.5rem;
  border: 2px solid #667eea;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #667eea;
  color: white;
}

.btn-map:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-map.secondary {
  background: transparent;
  color: #667eea;
}

.btn-map.secondary:hover {
  background: #667eea;
  color: white;
}

/* Icons */
.icon-location::before { content: '📍'; }
.icon-phone::before { content: '📞'; }
.icon-email::before { content: '✉️'; }
.icon-time::before { content: '🕒'; }
.icon-github::before { content: '⚡'; }
.icon-linkedin::before { content: '💼'; }
.icon-telegram::before { content: '✈️'; }
.icon-research::before { content: '🔬'; }
.icon-map::before { content: '🗺️'; }

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .contacts-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .contact-form-section {
    padding: 1.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .contact-card {
    padding: 1.5rem;
  }
  
  .social-links {
    justify-content: center;
  }
  
  .map-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-map {
    width: 200px;
  }
}
</style>
