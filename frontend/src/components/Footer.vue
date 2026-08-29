<template>
  <footer class="footer">
    <div class="footer-container">
      <!-- Main Footer Content -->
      <div class="footer-main">
        <div class="footer-section">
          <div class="footer-logo">
            <h3>Expert Polymer</h3>
            <p class="footer-subtitle">AI Analysis System</p>
          </div>
          <p class="footer-description">
            Инновационная экспертная система для анализа композитных материалов 
            с использованием технологий искусственного интеллекта и машинного обучения.
          </p>
          <div class="social-links">
            <a href="#" class="social-link" title="GitHub">
              <div class="icon-github"></div>
            </a>
            <a href="#" class="social-link" title="LinkedIn">
              <div class="icon-linkedin"></div>
            </a>
            <a href="#" class="social-link" title="Email">
              <div class="icon-email"></div>
            </a>
            <a href="#" class="social-link" title="ResearchGate">
              <div class="icon-research"></div>
            </a>
          </div>
        </div>

        <div class="footer-section">
          <h4>Навигация</h4>
          <ul class="footer-links">
            <li><a href="#home">Главная</a></li>
            <li><a href="#analysis">Анализ материалов</a></li>
            <li><a href="#materials">База материалов</a></li>
            <li><a href="#about">О системе</a></li>
            <li><a href="#documentation">Документация</a></li>
          </ul>
        </div>

        <div class="footer-section">
          <h4>Технологии</h4>
          <ul class="footer-links">
            <li><a href="#neural-networks">Нейронные сети</a></li>
            <li><a href="#computer-vision">Компьютерное зрение</a></li>
            <li><a href="#machine-learning">Машинное обучение</a></li>
            <li><a href="#data-analysis">Анализ данных</a></li>
            <li><a href="#api">API</a></li>
          </ul>
        </div>

        <div class="footer-section">
          <h4>Контакты</h4>
          <div class="contact-info">
            <div class="contact-item">
              <div class="contact-icon">
                <div class="icon-location"></div>
              </div>
              <div class="contact-text">
                <p>Казань, Россия</p>
                <p>ул. Петербургская 52, ИТ-Парк</p>
              </div>
            </div>
            <div class="contact-item">
              <div class="contact-icon">
                <div class="icon-phone"></div>
              </div>
              <div class="contact-text">
                <p>+7 (937) 368-96-93</p>
                <p>Пн-Пт: 9:00 - 18:00</p>
              </div>
            </div>
            <div class="contact-item">
              <div class="contact-icon">
                <div class="icon-email"></div>
              </div>
              <div class="contact-text">
                <p>info@expertpolymer.ru</p>
                <p>support@expertpolymer.ru</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Bottom -->
      <div class="footer-bottom">
        <div class="footer-bottom-content">
          <div class="copyright">
            <p>&copy; 2024 Expert Polymer. Все права защищены.</p>
            <p class="copyright-sub">Разработано с использованием Vue.js и современных веб-технологий</p>
          </div>
          <div class="footer-legal">
            <a href="#privacy">Политика конфиденциальности</a>
            <a href="#terms">Условия использования</a>
            <a href="#cookies">Cookies</a>
          </div>
        </div>
      </div>

      <!-- Decorative Elements -->
      <div class="footer-decoration">
        <div class="molecule-footer">
          <div class="atom-footer atom-1"></div>
          <div class="atom-footer atom-2"></div>
          <div class="atom-footer atom-3"></div>
          <div class="bond-footer bond-1"></div>
          <div class="bond-footer bond-2"></div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Логика компонента может быть добавлена здесь
</script>

<style scoped>
.footer {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="footer-grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="0.5" fill="white" opacity="0.05"/><circle cx="75" cy="75" r="0.5" fill="white" opacity="0.05"/></pattern></defs><rect width="100" height="100" fill="url(%23footer-grain)"/></svg>');
  opacity: 0.3;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 1;
}

.footer-main {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 3rem;
  padding: 4rem 0 2rem;
}

.footer-section h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #a8c8ec;
}

.footer-logo h3 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #ffffff;
}

.footer-subtitle {
  color: #a8c8ec;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.footer-description {
  line-height: 1.6;
  margin-bottom: 2rem;
  color: #cbd5e1;
  font-size: 0.95rem;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.social-link:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.icon-github::before { content: '⚡'; }
.icon-linkedin::before { content: '💼'; }
.icon-email::before { content: '✉️'; }
.icon-research::before { content: '🔬'; }

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 0.8rem;
}

.footer-links a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.3s ease;
}

.footer-links a:hover {
  color: #64b5f6;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.contact-icon {
  width: 20px;
  height: 20px;
  margin-top: 0.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-location::before { content: '📍'; }
.icon-phone::before { content: '📞'; }
.icon-email::before { content: '✉️'; }

.contact-text p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
  color: #cbd5e1;
}

.contact-text p:first-child {
  font-weight: 500;
  color: white;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2rem 0;
}

.footer-bottom-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.copyright p {
  margin: 0;
  font-size: 0.9rem;
  color: #cbd5e1;
}

.copyright-sub {
  font-size: 0.8rem !important;
  opacity: 0.7;
  margin-top: 0.3rem !important;
}

.footer-legal {
  display: flex;
  gap: 2rem;
}

.footer-legal a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.footer-legal a:hover {
  color: #64b5f6;
}

/* Decorative Elements */
.footer-decoration {
  position: absolute;
  top: 2rem;
  right: 2rem;
  opacity: 0.1;
  z-index: 0;
}

.molecule-footer {
  position: relative;
  width: 100px;
  height: 100px;
  animation: rotate-slow 30s linear infinite;
}

.atom-footer {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(45deg, #ffd700, #ffed4e);
}

.atom-footer.atom-1 { top: 10px; left: 50%; transform: translateX(-50%); }
.atom-footer.atom-2 { top: 50%; left: 10px; transform: translateY(-50%); }
.atom-footer.atom-3 { top: 50%; right: 10px; transform: translateY(-50%); }

.bond-footer {
  position: absolute;
  height: 1px;
  background: linear-gradient(90deg, #64b5f6, #42a5f5);
  transform-origin: left center;
}

.bond-footer.bond-1 { top: 20px; left: 50%; width: 50px; transform: translateX(-50%) rotate(60deg); }
.bond-footer.bond-2 { top: 50%; left: 20px; width: 50px; transform: translateY(-50%) rotate(-60deg); }

@keyframes rotate-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .footer-main {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .footer-bottom-content {
    flex-direction: column;
    text-align: center;
  }
  
  .footer-legal {
    justify-content: center;
  }
}
</style>
