<template>
  <div class="analysis-page">
    <!-- Header Section -->
    <section class="analysis-header">
      <div class="container">
        <div class="header-content">
          <h1 class="page-title">
            Анализ композитных материалов
          </h1>
          <p class="page-description">
            Загрузите изображение вашего композитного материала для проведения 
            глубокого анализа с использованием нейронных сетей
          </p>
        </div>
      </div>
    </section>

    <!-- Main Analysis Section -->
    <section class="analysis-main">
      <div class="container">
        <div class="analysis-container">
          <!-- Upload Section -->
          <div class="upload-section" v-if="!uploadedImage">
            <div class="upload-area" 
                 @click="triggerFileInput" 
                 @dragover.prevent 
                 @drop.prevent="handleDrop"
                 :class="{ 'drag-over': isDragOver }">
              <div class="upload-content">
                <div class="upload-icon">
                  <div class="icon-upload"></div>
                </div>
                <h3>Загрузите изображение</h3>
                <p>Перетащите файл сюда или нажмите для выбора</p>
                <div class="upload-formats">
                  <span>Поддерживаемые форматы: JPG, PNG, TIFF, BMP</span>
                </div>
                <button class="btn-upload" @click.stop="triggerFileInput">
                  Выбрать файл
                </button>
              </div>
              <input 
                ref="fileInput" 
                type="file" 
                accept="image/*" 
                @change="handleFileSelect" 
                style="display: none"
              />
            </div>
          </div>

          <!-- Image Preview Section -->
          <div class="preview-section" v-if="uploadedImage && !analysisStarted">
            <div class="image-container">
              <img :src="uploadedImage" alt="Загруженное изображение" class="preview-image" />
              <div class="image-overlay">
                <div class="image-info">
                  <h4>{{ fileName }}</h4>
                  <p>{{ fileSize }}</p>
                </div>
                <button class="btn-remove" @click="removeImage" title="Удалить изображение">
                  <div class="icon-remove"></div>
                </button>
              </div>
            </div>
            <p v-if="analysisError" class="analysis-error">{{ analysisError }}</p>
            <div class="preview-actions">
              <button class="btn-primary-large" @click="startAnalysis" :disabled="isAnalyzing">
                <span v-if="!isAnalyzing">Начать анализ</span>
                <span v-else class="loading-container">
                  <div class="loading"></div>
                  Анализируем...
                </span>
              </button>
            </div>
          </div>

          <!-- Analysis Progress Section -->
          <div class="progress-section" v-if="analysisStarted && !analysisComplete">
            <div class="progress-container">
              <div class="progress-header">
                <h3>Анализ в процессе</h3>
                <p>Нейронная сеть анализирует структуру материала...</p>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: progress + '%' }"></div>
              </div>
              <div class="progress-steps">
                <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
                  <div class="step-icon">1</div>
                  <span>Загрузка изображения</span>
                </div>
                <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
                  <div class="step-icon">2</div>
                  <span>Предобработка</span>
                </div>
                <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
                  <div class="step-icon">3</div>
                  <span>Нейронный анализ</span>
                </div>
                <div class="step" :class="{ active: currentStep >= 4, completed: currentStep > 4 }">
                  <div class="step-icon">4</div>
                  <span>Генерация отчета</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Results Section -->
          <div class="results-section" v-if="analysisComplete">
            <div class="results-header">
              <h2>Результаты анализа</h2>
              <p>Анализ завершен успешно</p>
            </div>
            
            <div class="results-content">
              <!-- Original Image -->
              <div class="result-image-container">
                <h3>Исходное изображение</h3>
                <div class="image-wrapper">
                  <img :src="uploadedImage" alt="Исходное изображение" class="result-image" />
                </div>
              </div>

              <!-- Analysis Results -->
              <div class="analysis-results">
                <h3>Результаты анализа</h3>
                <div class="results-grid">
                  <!-- Placeholder for analysis result image -->
                  <div class="result-visualization">
                    <div class="placeholder-result">
                      <div class="placeholder-icon">
                        <div class="icon-analysis"></div>
                      </div>
                      <img
                        v-if="processedImageUrl"
                        :src="processedImageUrl"
                        alt="Обработанное изображение"
                        class="result-image"
                      />
                      <p v-else>Обработанное изображение недоступно</p>
                    </div>
                  </div>

                  <!-- Analysis Data -->
                  <div class="analysis-data">
                    <div class="data-section">
                      <h4>Основные характеристики</h4>
                      <div class="data-item">
                        <span class="data-label">Результат:</span>
                        <span class="data-value">{{ analysisResult?.result || '—' }}</span>
                      </div>
                      <div class="data-item">
                        <span class="data-label">Уверенность:</span>
                        <span class="data-value">{{ confidencePercent }}%</span>
                      </div>
                      <div class="data-item">
                        <span class="data-label">Частиц обнаружено:</span>
                        <span class="data-value">{{ particlesDetected }}</span>
                      </div>
                      <div class="data-item">
                        <span class="data-label">Размер изображения:</span>
                        <span class="data-value">{{ imageDimensions }}</span>
                      </div>
                    </div>

                    <!-- Заключение нечёткой экспертной системы -->
                    <div v-if="expert" class="data-section">
                      <h4>Заключение экспертной системы</h4>
                      <div class="verdict-card" :class="verdictClass">
                        <div class="verdict-score">
                          {{ expert.score }}<span>/100</span>
                        </div>
                        <div class="verdict-text">
                          <div class="verdict-label">{{ verdictLabel }}</div>
                          <p>{{ expert.conclusion }}</p>
                        </div>
                      </div>
                      <div class="data-item">
                        <span class="data-label">Сферичность:</span>
                        <span class="data-value">{{ toPercent(expert.inputs.sphericity) }}%</span>
                      </div>
                      <div class="data-item">
                        <span class="data-label">Округлость:</span>
                        <span class="data-value">{{ toPercent(expert.inputs.smoothness) }}%</span>
                      </div>
                      <div class="data-item">
                        <span class="data-label">Однородность размеров:</span>
                        <span class="data-value">{{ toPercent(expert.inputs.uniformity) }}%</span>
                      </div>
                    </div>

                    <div v-if="composition.length" class="data-section">
                      <h4>Состав порошка</h4>
                      <div class="composition-list">
                        <div
                          v-for="item in composition"
                          :key="item.name"
                          class="composition-item"
                        >
                          <span class="composition-name">{{ item.label }}</span>
                          <div class="composition-bar">
                            <div
                              class="composition-fill"
                              :style="{ width: item.percent + '%' }"
                            ></div>
                          </div>
                          <span class="composition-value">{{ item.percent }}%</span>
                        </div>
                      </div>
                    </div>

                    <div v-if="morphology.length" class="data-section">
                      <h4>Морфология</h4>
                      <div
                        v-for="row in morphology"
                        :key="row.label"
                        class="data-item"
                      >
                        <span class="data-label">{{ row.label }}:</span>
                        <span class="data-value">{{ row.value }}</span>
                      </div>
                    </div>

                    <div v-if="!expert" class="data-section">
                      <h4>Заключение экспертной системы</h4>
                      <p class="expert-unavailable">
                        Экспертная оценка недоступна — сервер отвечает в режиме
                        заглушки (ML_BACKEND=mock).
                      </p>
                    </div>

                    <div class="data-section">
                      <h4>Модель</h4>
                      <div class="recommendations">
                        <p>{{ modelInfo }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="results-actions">
              <button class="btn-primary" @click="downloadReport">
                <div class="icon-download"></div>
                Скачать отчет
              </button>
              <button class="btn-secondary" @click="newAnalysis">
                <div class="icon-refresh"></div>
                Новый анализ
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { analyzeImage } from '@/api/analysis'
import { getAuthToken } from '@/api/auth'
import { staticUrl } from '@/api/client'

const uploadedImage = ref(null)
const selectedFile = ref(null)
const fileName = ref('')
const fileSize = ref('')
const isDragOver = ref(false)
const isAnalyzing = ref(false)
const analysisStarted = ref(false)
const analysisComplete = ref(false)
const analysisError = ref('')
const progress = ref(0)
const currentStep = ref(0)
const analysisResult = ref(null)
const processedImageUrl = ref(null)

const fileInput = ref(null)

const confidencePercent = computed(() => {
  const value = analysisResult.value?.confidence
  return value != null ? Math.round(value * 100) : 0
})

const particlesDetected = computed(() => {
  return analysisResult.value?.result_data?.particles_detected ?? 0
})

const detections = computed(() => {
  return analysisResult.value?.result_data?.detections ?? []
})

const imageDimensions = computed(() => {
  const width = analysisResult.value?.width
  const height = analysisResult.value?.height
  if (!width || !height) return '—'
  return `${width} × ${height}`
})

const modelInfo = computed(() => {
  const model = analysisResult.value?.result_data?.model
  if (!model) return 'Данные модели недоступны'
  return `${model.name} v${model.version} (${model.type})`
})

// --- Экспертная система -----------------------------------------------------
// Поля ниже приходят только когда backend работает с реальным ядром
// (ML_BACKEND=auto|expert_system). В режиме заглушки они отсутствуют.

const CLASS_LABELS = {
  dendritic: 'Дендритные',
  fragmented: 'Осколочные',
  spongy: 'Губчатые',
  spherical: 'Сферические',
  teardrop: 'Каплевидные',
}

const VERDICT_LABELS = {
  suitable: 'Пригоден',
  conditional: 'Условно пригоден',
  unsuitable: 'Не пригоден',
}

const expert = computed(() => analysisResult.value?.result_data?.expert ?? null)

const verdictLabel = computed(() => {
  const verdict = expert.value?.verdict
  return VERDICT_LABELS[verdict] ?? verdict ?? '—'
})

const verdictClass = computed(() => `verdict-${expert.value?.verdict ?? 'unknown'}`)

const toPercent = (value) => Math.round((value ?? 0) * 100)

const composition = computed(() => {
  const raw = analysisResult.value?.result_data?.composition
  if (!raw) return []

  return Object.entries(raw)
    .map(([name, percent]) => ({
      name,
      label: CLASS_LABELS[name] ?? name,
      percent,
    }))
    .filter((item) => item.percent > 0)
    .sort((a, b) => b.percent - a.percent)
})

const morphology = computed(() => {
  const data = analysisResult.value?.result_data
  if (!data || data.avg_circularity == null) return []

  const rows = [
    { label: 'Средняя округлость', value: data.avg_circularity },
    { label: 'Дисперсность', value: data.dispersity },
  ]

  const stats = data.size_stats
  if (stats) {
    rows.push({
      label: 'Диаметр частиц, px',
      value: `${stats.min_px} – ${stats.max_px}`,
    })
    rows.push({
      label: 'Средний диаметр, px',
      value: `${stats.mean_px} ± ${stats.std_px}`,
    })
  }

  return rows
})

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = (file) => {
  selectedFile.value = file
  analysisError.value = ''
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target.result
    fileName.value = file.name
    fileSize.value = formatFileSize(file.size)
  }
  reader.readAsDataURL(file)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const removeImage = () => {
  uploadedImage.value = null
  selectedFile.value = null
  fileName.value = ''
  fileSize.value = ''
  analysisError.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const startAnalysis = async () => {
  if (!selectedFile.value) return

  const token = getAuthToken()
  if (!token) {
    analysisError.value = 'Войдите в систему, чтобы запустить анализ'
    return
  }

  analysisStarted.value = true
  isAnalyzing.value = true
  analysisComplete.value = false
  analysisError.value = ''
  analysisResult.value = null
  processedImageUrl.value = null
  progress.value = 10
  currentStep.value = 1

  try {
    currentStep.value = 2
    progress.value = 40

    const result = await analyzeImage(selectedFile.value, token)

    currentStep.value = 3
    progress.value = 80

    analysisResult.value = result
    processedImageUrl.value = staticUrl(result.processed_image_path)

    currentStep.value = 4
    progress.value = 100
    analysisComplete.value = true
  } catch (error) {
    console.error('Analysis error:', error)
    analysisError.value = error.message || 'Ошибка анализа изображения'
    analysisStarted.value = false
  } finally {
    isAnalyzing.value = false
  }
}

const downloadReport = () => {
  // Placeholder for download functionality
  console.log('Downloading report...')
}

const newAnalysis = () => {
  uploadedImage.value = null
  selectedFile.value = null
  fileName.value = ''
  fileSize.value = ''
  analysisStarted.value = false
  analysisComplete.value = false
  analysisResult.value = null
  processedImageUrl.value = null
  analysisError.value = ''
  progress.value = 0
  currentStep.value = 0
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Event listeners for drag and drop
const handleDragOver = (e) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  isDragOver.value = false
}

onMounted(() => {
  document.addEventListener('dragover', handleDragOver)
  document.addEventListener('dragleave', handleDragLeave)
})

onUnmounted(() => {
  document.removeEventListener('dragover', handleDragOver)
  document.removeEventListener('dragleave', handleDragLeave)
})
</script>

<style scoped>
.analysis-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* Header Section */
.analysis-header {
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

/* Main Analysis Section */
.analysis-main {
  padding: 4rem 0;
}

.analysis-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* Upload Section */
.upload-area {
  border: 3px dashed #cbd5e1;
  border-radius: 20px;
  padding: 4rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  position: relative;
  overflow: hidden;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.1);
}

.upload-content {
  position: relative;
  z-index: 1;
}

.upload-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
}

.icon-upload::before { content: '📁'; }

.upload-area h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e3c72;
  margin-bottom: 1rem;
}

.upload-area p {
  color: #64748b;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.upload-formats {
  margin-bottom: 2rem;
}

.upload-formats span {
  color: #94a3b8;
  font-size: 0.9rem;
}

.btn-upload {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-upload:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Preview Section */
.preview-section {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.image-container {
  position: relative;
  margin-bottom: 2rem;
  border-radius: 15px;
  overflow: hidden;
  background: #f8fafc;
}

.preview-image {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  display: block;
}

.image-overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.image-info {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.image-info h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.image-info p {
  margin: 0;
  font-size: 0.8rem;
  opacity: 0.8;
}

.btn-remove {
  background: rgba(255, 107, 107, 0.9);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-remove:hover {
  background: rgba(255, 107, 107, 1);
  transform: scale(1.1);
}

.icon-remove::before { content: '✕'; }

.analysis-error {
  margin-top: 1rem;
  color: #c0392b;
  text-align: center;
}

.preview-actions {
  text-align: center;
}

.btn-primary-large {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  border: none;
  padding: 1.2rem 3rem;
  border-radius: 30px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary-large:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
}

.btn-primary-large:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Progress Section */
.progress-section {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.progress-header h3 {
  font-size: 1.8rem;
  color: #1e3c72;
  margin-bottom: 0.5rem;
}

.progress-header p {
  color: #64748b;
  margin-bottom: 2rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 3rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.step.active {
  opacity: 1;
  color: #667eea;
}

.step.completed {
  opacity: 1;
  color: #10b981;
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s ease;
}

.step.active .step-icon {
  background: #667eea;
  color: white;
}

.step.completed .step-icon {
  background: #10b981;
  color: white;
}

.step span {
  font-size: 0.9rem;
  font-weight: 500;
}

/* Results Section */
.results-section {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.results-header {
  text-align: center;
  margin-bottom: 3rem;
}

.results-header h2 {
  font-size: 2.5rem;
  color: #1e3c72;
  margin-bottom: 0.5rem;
}

.results-header p {
  color: #10b981;
  font-weight: 600;
  font-size: 1.1rem;
}

.results-content {
  margin-bottom: 3rem;
}

.result-image-container {
  margin-bottom: 3rem;
}

.result-image-container h3 {
  font-size: 1.5rem;
  color: #1e3c72;
  margin-bottom: 1rem;
}

.image-wrapper {
  border-radius: 15px;
  overflow: hidden;
  background: #f8fafc;
}

.result-image {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  display: block;
}

.analysis-results h3 {
  font-size: 1.5rem;
  color: #1e3c72;
  margin-bottom: 2rem;
}

.results-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

.result-visualization {
  background: #f8fafc;
  border-radius: 15px;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.placeholder-result {
  text-align: center;
  color: #64748b;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
}

.icon-analysis::before { content: '🔬'; }

.placeholder-result p {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.placeholder-result small {
  color: #94a3b8;
}

.analysis-data {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.data-section h4 {
  font-size: 1.2rem;
  color: #1e3c72;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.data-label {
  font-weight: 500;
  color: #64748b;
}

.data-value {
  font-weight: 600;
  color: #1e3c72;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* --- Заключение экспертной системы --- */

.verdict-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  border-left: 5px solid #94a3b8;
  background: #f1f5f9;
  margin-bottom: 1rem;
}

.verdict-card.verdict-suitable {
  border-left-color: #10b981;
  background: #ecfdf5;
}

.verdict-card.verdict-conditional {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.verdict-card.verdict-unsuitable {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.verdict-score {
  font-size: 2rem;
  font-weight: 700;
  color: #1e3c72;
  line-height: 1;
  white-space: nowrap;
}

.verdict-score span {
  font-size: 1rem;
  font-weight: 500;
  color: #64748b;
}

.verdict-label {
  font-weight: 700;
  color: #1e3c72;
  margin-bottom: 0.25rem;
}

.verdict-text p {
  margin: 0;
  color: #475569;
  font-size: 0.9rem;
}

.expert-unavailable {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

/* --- Состав порошка --- */

.composition-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.composition-item {
  display: grid;
  grid-template-columns: 7.5rem 1fr 3rem;
  align-items: center;
  gap: 0.75rem;
}

.composition-name {
  color: #64748b;
  font-size: 0.9rem;
}

.composition-bar {
  height: 8px;
  border-radius: 4px;
  background: #e2e8f0;
  overflow: hidden;
}

.composition-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #2a5298, #1e3c72);
}

.composition-value {
  text-align: right;
  font-weight: 600;
  color: #1e3c72;
  font-size: 0.9rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.feature-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #10b981;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
}

.recommendations {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 1rem;
}

.recommendations p {
  margin: 0;
  color: #0369a1;
  line-height: 1.6;
}

.results-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

.icon-download::before { content: '⬇️'; }
.icon-refresh::before { content: '🔄'; }

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .progress-steps {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .results-actions {
    flex-direction: column;
  }
}
</style>
