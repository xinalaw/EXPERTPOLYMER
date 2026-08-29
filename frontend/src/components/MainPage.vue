<template>
  <main class="main-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-container">
        <div class="hero-content">
          <h1 class="hero-title">
            Экспертная система анализа
            <span class="highlight">композитных материалов</span>
          </h1>
          <p class="hero-description">
            Инновационная нейронная сеть для глубокого анализа структуры, свойств 
            и характеристик полимерных композитов с использованием технологий 
            машинного обучения и компьютерного зрения.
          </p>
          <div class="hero-actions">
            <button class="btn-primary-large" @click="navigateTo('analysis')">Начать анализ</button>
            <button class="btn-secondary">Узнать больше</button>
          </div>
        </div>
        <div class="hero-visual">
          <div class="molecule-animation">
            <div class="atom atom-1"></div>
            <div class="atom atom-2"></div>
            <div class="atom atom-3"></div>
            <div class="bond bond-1"></div>
            <div class="bond bond-2"></div>
            <div class="bond bond-3"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="container">
        <h2 class="section-title">Возможности системы</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <div class="icon-brain"></div>
            </div>
            <h3>Нейронный анализ</h3>
            <p>Глубокое обучение для распознавания микроструктур и выявления дефектов в композитных материалах</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <div class="icon-microscope"></div>
            </div>
            <h3>Микроскопический анализ</h3>
            <p>Обработка изображений с электронного и оптического микроскопов для детального изучения структуры</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <div class="icon-chart"></div>
            </div>
            <h3>Прогнозирование свойств</h3>
            <p>Предсказание механических, термических и химических свойств на основе структурного анализа</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <div class="icon-database"></div>
            </div>
            <h3>База знаний</h3>
            <p>Обширная база данных полимерных композитов и их характеристик для сравнения и анализа</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Technology Section -->
    <section class="technology">
      <div class="container">
        <div class="tech-content">
          <div class="tech-text">
            <h2>Передовые технологии</h2>
            <p class="tech-description">
              Наша система использует современные алгоритмы машинного обучения, 
              включая сверточные нейронные сети (CNN), рекуррентные нейронные сети (RNN) 
              и трансформеры для анализа сложных структур композитных материалов.
            </p>
            <div class="tech-stats">
              <div class="stat">
                <span class="stat-number">95%</span>
                <span class="stat-label">Точность анализа</span>
              </div>
              <div class="stat">
                <span class="stat-number">10k+</span>
                <span class="stat-label">Образцов в базе</span>
              </div>
              <div class="stat">
                <span class="stat-number">10s</span>
                <span class="stat-label">Среднее время обработки</span>
              </div>
            </div>
          </div>
          <div class="tech-visual">
            <div class="neural-network">
              <div class="layer layer-1">
                <div class="node"></div>
                <div class="node"></div>
                <div class="node"></div>
              </div>
              <div class="layer layer-2">
                <div class="node"></div>
                <div class="node"></div>
                <div class="node"></div>
                <div class="node"></div>
              </div>
              <div class="layer layer-3">
                <div class="node"></div>
                <div class="node"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="container">
        <div class="cta-content">
          <h2>Готовы начать анализ?</h2>
          <p>Загрузите изображение вашего композитного материала и получите детальный анализ за секунды</p>
          <div class="cta-actions">
            <button class="btn-primary-large" @click="navigateTo('analysis')">Загрузить образец</button>
            <button class="btn-outline">Связаться с нами</button>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
// Emits
const emit = defineEmits(['navigate'])

// Methods
const navigateTo = (page) => {
  emit('navigate', page)
}
</script>

<style scoped>
.main-page {
  min-height: 100%;
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 4rem 0;
  color: white;
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  letter-spacing: -1px;
}

.highlight {
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 2.5rem;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary-large {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 30px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
}

.btn-primary-large:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 1rem 2rem;
  border-radius: 30px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.6);
}

/* Molecule Animation */
.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.molecule-animation {
  position: relative;
  width: 200px;
  height: 200px;
  animation: rotate 20s linear infinite;
}

.atom {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
}

.atom-1 { top: 20px; left: 50%; transform: translateX(-50%); }
.atom-2 { top: 50%; left: 20px; transform: translateY(-50%); }
.atom-3 { top: 50%; right: 20px; transform: translateY(-50%); }

.bond {
  position: absolute;
  height: 2px;
  background: linear-gradient(90deg, #64b5f6, #42a5f5);
  transform-origin: left center;
}

.bond-1 { top: 30px; left: 50%; width: 100px; transform: translateX(-50%) rotate(60deg); }
.bond-2 { top: 50%; left: 30px; width: 100px; transform: translateY(-50%) rotate(-60deg); }
.bond-3 { top: 50%; right: 30px; width: 100px; transform: translateY(-50%) rotate(60deg); }

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Features Section */
.features {
  padding: 6rem 0;
  background: #f8fafc;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e3c72;
  margin-bottom: 3rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2.5rem 2rem;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.icon-brain, .icon-microscope, .icon-chart, .icon-database {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.feature-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e3c72;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #64748b;
  line-height: 1.6;
}

/* Technology Section */
.technology {
  padding: 6rem 0;
  background: white;
}

.tech-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.tech-text h2 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e3c72;
  margin-bottom: 1.5rem;
}

.tech-description {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #64748b;
  margin-bottom: 2rem;
}

.tech-stats {
  display: flex;
  gap: 2rem;
}

.stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2.5rem;
  font-weight: 800;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

/* Neural Network Visualization */
.tech-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.neural-network {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.layer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.node {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

.node:nth-child(2) { animation-delay: 0.2s; }
.node:nth-child(3) { animation-delay: 0.4s; }
.node:nth-child(4) { animation-delay: 0.6s; }

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; }
}

/* CTA Section */
.cta {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  padding: 4rem 0;
  color: white;
  text-align: center;
}

.cta-content h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.cta-content p {
  font-size: 1.2rem;
  margin-bottom: 2.5rem;
  opacity: 0.9;
}

.cta-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 1rem 2rem;
  border-radius: 30px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.6);
}
</style>
