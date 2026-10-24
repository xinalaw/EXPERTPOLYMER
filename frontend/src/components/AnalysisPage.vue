<script setup lang="ts">
import { ref } from 'vue'
import { useAnalysis } from '@/composables/useAnalysis'
import { downloadReport } from '@/utils/files'
import FileUploader from './analysis/FileUploader.vue'
import AnalysisResult from './analysis/AnalysisResult.vue'
import ResultImage from './ui/ResultImage.vue'
const { file, preview, result, phase, error, busy, selectFile, start, cancel, reset } =
  useAnalysis()
const localError = ref('')
async function select(candidate: File) {
  localError.value = ''
  await selectFile(candidate)
}
function download() {
  try {
    if (result.value) downloadReport(result.value)
  } catch {
    localError.value = 'Не удалось скачать отчёт. Попробуйте повторить.'
  }
}
</script>
<template>
  <div class="page-shell">
    <header class="page-heading">
      <h1>Анализ композитных материалов</h1>
      <p>Загрузите микроскопический снимок для анализа структуры материала.</p>
    </header>
    <aside class="notice" aria-label="Требования к изображениям">
      <strong>Анализ в режиме прототипа</strong>
      <p>
        Используйте демонстрационные СЭМ-снимки отдельных частиц на тёмном фоне, созданные
        встроенным генератором. Фотографии предметов и другие произвольные изображения не подходят
        для проверки модели.
      </p>
      <RouterLink class="btn btn-secondary" to="/generation">Сгенерировать снимок</RouterLink>
    </aside>
    <p v-if="error || localError" class="notice error" role="alert">{{ error || localError }}</p>
    <FileUploader v-if="!file" :busy="busy" @select="select" @invalid="localError = $event" />
    <section v-else-if="phase !== 'complete'" class="panel">
      <h2>{{ file.name }}</h2>
      <p class="muted">{{ (file.size / 1024 / 1024).toFixed(2) }} МБ</p>
      <ResultImage :src="preview" alt="Выбранное изображение" />
      <div v-if="phase === 'running'" class="analysis-progress" role="status" aria-live="polite">
        <progress aria-label="Выполняется анализ" />
        <p>
          Изображение обрабатывается. Можно перейти на другую страницу — результат останется здесь.
        </p>
        <button class="btn btn-secondary" @click="cancel">Остановить ожидание</button>
      </div>
      <div v-else class="actions">
        <button class="btn btn-primary" :disabled="busy" @click="start">Начать анализ</button
        ><button class="btn btn-secondary" @click="reset">Выбрать другое изображение</button>
      </div>
    </section>
    <section v-if="result" class="panel">
      <h2 tabindex="-1">Результаты анализа</h2>
      <p role="status">
        Обработка завершена. Результат прототипа может содержать ошибки; проверьте его со
        специалистом.
      </p>
      <AnalysisResult :result="result" :original="preview" />
      <div class="actions">
        <button class="btn btn-primary" @click="download">Скачать отчёт (JSON)</button
        ><button class="btn btn-secondary" @click="reset">Новый анализ</button
        ><RouterLink class="btn btn-secondary" to="/history">История анализов</RouterLink>
      </div>
    </section>
  </div>
</template>
<style scoped>
.analysis-progress {
  margin-top: 1.5rem;
}
progress {
  width: 100%;
  accent-color: var(--primary);
}
</style>
