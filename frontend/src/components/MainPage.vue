<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import FeatureGrid from './ui/FeatureGrid.vue'

const headerHeight = ref(0)
let headerObserver: ResizeObserver | undefined
onMounted(() => {
  const header = document.querySelector<HTMLElement>('.navbar')
  if (!header) return
  const updateHeight = () => {
    headerHeight.value = header.getBoundingClientRect().height
  }
  updateHeight()
  headerObserver = new ResizeObserver(updateHeight)
  headerObserver.observe(header)
})
onBeforeUnmount(() => headerObserver?.disconnect())

const features = [
  {
    title: 'Анализ снимков',
    text: 'Загрузка микроскопических изображений и распознавание частиц материала.',
    symbol: '◉',
  },
  {
    title: 'Морфология частиц',
    text: 'Размеры, округлость и распределение частиц по результатам обработки.',
    symbol: '⌁',
  },
  {
    title: 'Экспертная оценка',
    text: 'Заключение о пригодности порошка на основе рассчитанных характеристик.',
    symbol: '◇',
  },
  {
    title: 'История исследований',
    text: 'Просмотр сохранённых результатов и скачивание подробного отчёта.',
    symbol: '▤',
  },
]
</script>
<template>
  <div class="main-page">
    <section class="hero" :style="{ '--header-height': headerHeight + 'px' }">
      <div class="container hero-layout">
        <div>
          <p class="eyebrow">GranulAI</p>
          <h1>Экспертная система анализа <span>композитных материалов</span></h1>
          <p class="hero-description">
            От микроскопического снимка — к характеристикам частиц и экспертному заключению.
            Исследуйте структуру материала и сохраняйте результаты в одном месте.
          </p>
          <div class="actions">
            <RouterLink class="btn hero-primary" to="/analysis">Начать анализ</RouterLink
            ><RouterLink class="btn hero-secondary" to="/generation"
              >Сгенерировать снимок</RouterLink
            >
          </div>
        </div>
        <div class="molecule" aria-hidden="true">
          <div class="orbit orbit-one"></div>
          <div class="orbit orbit-two"></div>
          <div class="orbit orbit-three"></div>
          <div class="nucleus"></div>
          <i class="particle particle-one"></i><i class="particle particle-two"></i
          ><i class="particle particle-three"></i>
        </div>
      </div>
    </section>
    <section class="container home-section">
      <h2>Возможности системы</h2>
      <FeatureGrid :items="features" />
    </section>
    <section class="container home-section">
      <div class="panel workflow">
        <h2>От изображения к результату</h2>
        <ol>
          <li><strong>Выберите снимок.</strong> JPG, PNG, TIFF или BMP размером до 20 МБ.</li>
          <li>
            <strong>Запустите анализ.</strong> Система обработает изображение и рассчитает
            характеристики.
          </li>
          <li>
            <strong>Изучите результат.</strong> Просмотрите изображение, оценку и сохраните
            JSON-отчёт.
          </li>
        </ol>
      </div>
    </section>
    <section class="container home-section">
      <div class="cta">
        <h2>Готовы исследовать образец?</h2>
        <p>Войдите в систему и загрузите микроскопический снимок.</p>
        <div class="actions">
          <RouterLink to="/analysis" class="btn btn-primary">Загрузить образец</RouterLink
          ><RouterLink to="/contacts" class="btn btn-secondary">Связаться с нами</RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>
<style scoped>
.hero {
  min-height: calc(100vh - var(--header-height, 0px));
  min-height: calc(100dvh - var(--header-height, 0px));
  display: flex;
  align-items: center;
  background: var(--brand-gradient);
  color: white;
  padding: clamp(3rem, 7vw, 6rem) 0;
  overflow: hidden;
}
.hero-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
  align-items: center;
  gap: 3rem;
}
.hero h1 {
  max-width: 800px;
  font-size: clamp(2rem, 4vw, 3.5rem);
}
.hero h1 span {
  color: #fff0b3;
}
.hero-description {
  font-size: 1.1rem;
  color: #f4f2ff;
  max-width: 680px;
}
.eyebrow {
  font-size: 0.85rem;
  letter-spacing: 0.16em;
  font-weight: 700;
}
.hero-primary {
  background: white;
  color: #3f4091;
}
.hero-secondary {
  color: white;
  border-color: #ffffffaa;
}
.hero-secondary:hover {
  background: #ffffff1a;
}
.home-section {
  padding-block: 2.5rem;
}
.workflow ol {
  display: grid;
  gap: 1rem;
  padding-left: 1.5rem;
  margin-bottom: 0;
}
.cta {
  text-align: center;
  padding: 2rem;
  border-radius: var(--radius);
  background: #eef0fc;
}
.cta .actions {
  justify-content: center;
}
.molecule {
  position: relative;
  width: min(320px, 100%);
  aspect-ratio: 1;
  margin: auto;
}
.orbit {
  position: absolute;
  inset: 15%;
  border: 2px solid #ffffff80;
  border-radius: 50%;
}
.orbit-one {
  transform: rotate(35deg) scaleX(0.4);
}
.orbit-two {
  transform: rotate(-35deg) scaleX(0.4);
}
.orbit-three {
  transform: rotate(90deg) scaleX(0.4);
}
.nucleus {
  position: absolute;
  inset: 40%;
  border-radius: 50%;
  background: #fff0b3;
  box-shadow: 0 0 60px #fff0b366;
}
.particle {
  position: absolute;
  width: 22px;
  height: 22px;
  background: #d4f3ff;
  border-radius: 50%;
  animation: particle-glow 3s ease-in-out infinite alternate;
}
.particle-one {
  top: 20%;
  left: 26%;
}
.particle-two {
  top: 50%;
  right: 12%;
}
.particle-three {
  bottom: 20%;
  left: 23%;
}
@keyframes particle-glow {
  to {
    box-shadow: 0 0 25px #d4f3ff;
  }
}
@media (max-width: 760px) {
  .hero-layout {
    grid-template-columns: 1fr;
  }
  .molecule {
    width: 190px;
  }
  .hero {
    padding-block: 2.5rem;
  }
  .home-section {
    padding-block: 1.5rem;
  }
}
</style>
