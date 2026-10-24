<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '@/api/client'
import { useAnalysis } from '@/composables/useAnalysis'

const router = useRouter()
const analysis = useAnalysis()
const image = ref('')
const busy = ref(false)
const error = ref('')
const controller = new AbortController()
onBeforeUnmount(() => controller.abort())
async function generate() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    const result = await apiFetch<{ image: string }>('/api/generate', {
      method: 'POST',
      signal: controller.signal,
    })
    image.value = 'data:image/png;base64,' + result.image
  } catch (cause) {
    if (!controller.signal.aborted)
      error.value = cause instanceof Error ? cause.message : 'Не удалось создать снимок.'
  } finally {
    busy.value = false
  }
}
async function analyze() {
  error.value = ''
  try {
    const blob = await (await fetch(image.value)).blob()
    await analysis.selectFile(new File([blob], 'synthetic-sem.png', { type: 'image/png' }))
    if (analysis.error.value) {
      error.value = analysis.error.value
      return
    }
    await router.push('/analysis')
  } catch {
    error.value = 'Не удалось передать снимок на анализ. Скачайте PNG и загрузите его вручную.'
  }
}
</script>
<template>
  <div class="page-shell">
    <header class="page-heading">
      <h1>Генерация изображений</h1>
      <p>Синтетические СЭМ-снимки для демонстрации анализа частиц.</p>
    </header>
    <section class="panel">
      <h2>Демонстрационный образец</h2>
      <p>
        Генератор создаёт случайный снимок 224 × 224 пикселя с частицами разных форм на тёмном фоне.
        Это искусственное изображение, а не результат исследования материала. Точность распознавания
        прототипом не гарантируется.
      </p>
      <p v-if="error" class="notice error" role="alert">{{ error }}</p>
      <p v-if="busy" role="status">Создаём снимок…</p>
      <img
        v-if="image"
        :src="image"
        width="224"
        height="224"
        alt="Синтетический СЭМ-снимок частиц"
      />
      <div class="actions">
        <button class="btn btn-primary" :disabled="busy" @click="generate">
          {{ busy ? 'Генерация…' : image ? 'Создать другой снимок' : 'Сгенерировать снимок' }}
        </button>
        <a v-if="image" class="btn btn-secondary" :href="image" download="synthetic-sem.png"
          >Скачать PNG</a
        >
        <button
          v-if="image"
          class="btn btn-secondary"
          :disabled="busy || analysis.busy.value"
          @click="analyze"
        >
          Использовать для анализа
        </button>
      </div>
      <p v-if="analysis.file.value" class="muted">
        При выборе нового снимка текущий образец и результат анализа будут заменены.
      </p>
    </section>
  </div>
</template>
