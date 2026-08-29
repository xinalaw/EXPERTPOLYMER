<template>
  <div class="history-page">
    <!-- Header Section -->
    <section class="history-header">
      <div class="container">
        <div class="header-content">
          <h1 class="page-title">История анализов</h1>
          <p class="page-description">
            Просмотр всех выполненных анализов изображений композитных материалов
          </p>
        </div>
      </div>
    </section>

    <!-- Main History Section -->
    <section class="history-main">
      <div class="container">
        <!-- Filter Section -->
        <div class="filter-section">
          <div class="filter-group">
            <label for="dateFilter">Фильтр по дате:</label>
            <input 
              v-model="selectedDate" 
              type="date" 
              id="dateFilter"
              @change="loadHistory"
              class="filter-input"
            />
          </div>
          <button 
            class="btn-refresh" 
            @click="loadHistory"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">🔄 Обновить</span>
            <span v-else>⏳ Загрузка...</span>
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Загрузка истории анализов...</p>
        </div>

        <!-- Error State -->
        <div v-if="errorMessage" class="error-state">
          <p class="error-message">{{ errorMessage }}</p>
          <button class="btn-retry" @click="loadHistory">Повторить</button>
        </div>

        <!-- Empty State -->
        <div v-if="!isLoading && !errorMessage && analysisHistory.length === 0" class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>История анализов пуста</h3>
          <p>Выполните анализ изображения, чтобы он отобразился здесь</p>
        </div>

        <!-- History List -->
        <div v-if="!isLoading && !errorMessage && analysisHistory.length > 0" class="history-list">
          <div 
            v-for="(analysis, index) in analysisHistory" 
            :key="analysis.id"
            class="history-card"
            :class="{ 'expanded': expandedCards.includes(analysis.id) }"
          >
            <!-- Card Header -->
            <div class="card-header" @click="toggleCard(analysis.id)">
              <div class="card-info">
                <h3 class="card-title">{{ analysis.original_filename }}</h3>
                <p class="card-date">{{ formatDate(analysis.created_at) }}</p>
              </div>
              <div class="card-result">
                <span class="result-badge" :class="analysis.result.toLowerCase()">
                  {{ analysis.result }}
                </span>
                <span class="confidence-badge">
                  {{ Math.round(analysis.confidence * 100) }}%
                </span>
              </div>
              <button class="expand-btn">
                {{ expandedCards.includes(analysis.id) ? '▼' : '▶' }}
              </button>
            </div>

            <!-- Card Content (Expandable) -->
            <div v-if="expandedCards.includes(analysis.id)" class="card-content">
              <!-- Images Preview -->
              <div class="images-section">
                <div class="image-preview">
                  <h4>Исходное изображение</h4>
                  <img 
                    :src="staticUrl(analysis.image_path)" 
                    :alt="analysis.original_filename"
                    class="preview-image"
                  />
                </div>
                <div v-if="analysis.processed_image_path" class="image-preview">
                  <h4>Обработанное изображение</h4>
                  <img 
                    :src="staticUrl(analysis.processed_image_path)" 
                    :alt="'Processed - ' + analysis.original_filename"
                    class="preview-image"
                  />
                </div>
              </div>

              <!-- Analysis Data -->
              <div class="analysis-details">
                <div class="details-section">
                  <h4>Характеристики</h4>
                  <div class="detail-row">
                    <span class="detail-label">Размер:</span>
                    <span class="detail-value">{{ analysis.width }} × {{ analysis.height }} px</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Результат:</span>
                    <span class="detail-value">{{ analysis.result }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Уверенность:</span>
                    <span class="detail-value">{{ Math.round(analysis.confidence * 100) }}%</span>
                  </div>
                  <div v-if="analysis.result_data" class="detail-row">
                    <span class="detail-label">Частиц обнаружено:</span>
                    <span class="detail-value">{{ analysis.result_data.particles_detected }}</span>
                  </div>
                </div>

                <!-- Model Info -->
                <div v-if="analysis.result_data?.model" class="details-section">
                  <h4>Информация о модели</h4>
                  <div class="detail-row">
                    <span class="detail-label">Модель:</span>
                    <span class="detail-value">{{ analysis.result_data.model.name }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Версия:</span>
                    <span class="detail-value">{{ analysis.result_data.model.version }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Тип:</span>
                    <span class="detail-value">{{ analysis.result_data.model.type }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Время обработки:</span>
                    <span class="detail-value">{{ Math.round(analysis.result_data.processing_time_ms) }} ms</span>
                  </div>
                </div>

                <!-- Detections -->
                <div v-if="analysis.result_data?.detections?.length" class="details-section">
                  <h4>Обнаруженные объекты ({{ analysis.result_data.detections.length }})</h4>
                  <div class="detections-list">
                    <div 
                      v-for="(detection, i) in analysis.result_data.detections.slice(0, 5)"
                      :key="i"
                      class="detection-item"
                    >
                      <span class="detection-label">{{ detection.label }}</span>
                      <div class="detection-confidence">{{ Math.round(detection.confidence * 100) }}%</div>
                    </div>
                    <div v-if="analysis.result_data.detections.length > 5" class="detection-item muted">
                      ... и ещё {{ analysis.result_data.detections.length - 5 }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Card Actions -->
              <div class="card-actions">
                <button 
                  class="btn-download"
                  @click="downloadReport(analysis.id)"
                  :disabled="downloadingId === analysis.id"
                >
                  {{ downloadingId === analysis.id ? '⏳' : '⬇' }} 
                  {{ downloadingId === analysis.id ? 'Загрузка...' : 'Скачать отчет' }}
                </button>
                <button 
                  class="btn-delete"
                  @click="deleteAnalysis(analysis.id)"
                  :disabled="deletingId === analysis.id"
                >
                  {{ deletingId === analysis.id ? '⏳' : '🗑' }}
                  {{ deletingId === analysis.id ? 'Удаление...' : 'Удалить' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalCount > limit" class="pagination">
            <button 
              @click="previousPage"
              :disabled="offset === 0"
              class="btn-pagination"
            >
              ← Назад
            </button>
            <span class="pagination-info">
              {{ offset + 1 }} - {{ Math.min(offset + limit, totalCount) }} из {{ totalCount }}
            </span>
            <button 
              @click="nextPage"
              :disabled="offset + limit >= totalCount"
              class="btn-pagination"
            >
              Вперед →
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAnalysisHistory, downloadAnalysisReport, deleteAnalysisResult } from '@/api/analysis'
import { getAuthToken } from '@/api/auth'
import { staticUrl } from '@/api/client'

// Reactive state
const analysisHistory = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const expandedCards = ref([])
const selectedDate = ref('')
const downloadingId = ref(null)
const deletingId = ref(null)

// Pagination
const limit = ref(20)
const offset = ref(0)
const totalCount = ref(0)

// Methods
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }
  return date.toLocaleDateString('ru-RU', options)
}

const toggleCard = (id) => {
  const index = expandedCards.value.indexOf(id)
  if (index > -1) {
    expandedCards.value.splice(index, 1)
  } else {
    expandedCards.value.push(id)
  }
}

const loadHistory = async () => {
  const token = getAuthToken()
  if (!token) {
    errorMessage.value = 'Требуется авторизация'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const params = {
      limit: limit.value,
      offset: offset.value,
    }

    if (selectedDate.value) {
      params.date = selectedDate.value
    }

    const results = await getAnalysisHistory(params, token)
    
    analysisHistory.value = results
    // Примерное значение, так как API может не возвращать totalCount
    totalCount.value = Math.max(results.length + offset.value, 100)
  } catch (error) {
    console.error('Error loading history:', error)
    errorMessage.value = error.message || 'Ошибка загрузки истории анализов'
  } finally {
    isLoading.value = false
  }
}

const downloadReport = async (resultId) => {
  try {
    downloadingId.value = resultId
    const blob = await downloadAnalysisReport(resultId, getAuthToken())
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analysis-report-${resultId}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download error:', error)
    alert(`Ошибка загрузки отчета: ${error.message}`)
  } finally {
    downloadingId.value = null
  }
}

const deleteAnalysis = async (resultId) => {
  if (!confirm('Вы уверены? Этот анализ будет удален навсегда.')) {
    return
  }

  try {
    deletingId.value = resultId
    await deleteAnalysisResult(resultId, getAuthToken())
    
    analysisHistory.value = analysisHistory.value.filter(a => a.id !== resultId)
    expandedCards.value = expandedCards.value.filter(id => id !== resultId)
  } catch (error) {
    console.error('Delete error:', error)
    alert(`Ошибка удаления: ${error.message}`)
  } finally {
    deletingId.value = null
  }
}

const previousPage = () => {
  offset.value = Math.max(0, offset.value - limit.value)
  loadHistory()
}

const nextPage = () => {
  offset.value += limit.value
  loadHistory()
}

// Load on mount
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* Header Section */
.history-header {
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

/* Main History Section */
.history-main {
  padding: 4rem 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Filter Section */
.filter-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.filter-group label {
  font-weight: 600;
  color: #1e3c72;
}

.filter-input {
  padding: 0.75rem 1rem;
  border: 2px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.filter-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn-refresh {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.btn-refresh:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #64748b;
  font-size: 1.1rem;
}

/* Error State */
.error-state {
  background: #fee2e2;
  border-left: 4px solid #ef4444;
  padding: 2rem;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 2rem;
}

.error-message {
  color: #991b1b;
  margin-bottom: 1rem;
  font-weight: 600;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}

.btn-retry:hover {
  background: #dc2626;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #1e3c72;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #64748b;
}

/* History List */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.history-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  overflow: hidden;
  transition: all 0.3s ease;
}

.history-card:hover {
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  transition: background 0.2s ease;
}

.card-header:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
}

.card-info {
  flex: 1;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e3c72;
  margin-bottom: 0.25rem;
  word-break: break-word;
}

.card-date {
  font-size: 0.9rem;
  color: #64748b;
}

.card-result {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.result-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
}

.result-badge.good {
  background: #dcfce7;
  color: #166534;
}

.result-badge.ok {
  background: #fef3c7;
  color: #92400e;
}

.result-badge.bad {
  background: #fee2e2;
  color: #991b1b;
}

.confidence-badge {
  background: #e0e7ff;
  color: #3730a3;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
}

.expand-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #667eea;
  padding: 0.5rem;
  transition: transform 0.2s ease;
}

/* Card Content */
.card-content {
  padding: 2rem;
  border-top: 1px solid #e2e8f0;
}

.images-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.image-preview {
  text-align: center;
}

.image-preview h4 {
  color: #1e3c72;
  font-weight: 600;
  margin-bottom: 1rem;
}

.preview-image {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
}

.analysis-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.details-section {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 1rem;
  border-radius: 8px;
}

.details-section h4 {
  color: #1e3c72;
  font-weight: 700;
  margin-bottom: 1rem;
  border-bottom: 2px solid #cbd5e1;
  padding-bottom: 0.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #cbd5e1;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: #475569;
}

.detail-value {
  color: #1e3c72;
  font-weight: 500;
}

.detections-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.detection-item.muted {
  color: #94a3b8;
  font-style: italic;
}

.detection-label {
  font-weight: 500;
  color: #1e3c72;
}

.detection-confidence {
  background: #e0e7ff;
  color: #3730a3;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.btn-download,
.btn-delete {
  flex: 1;
  min-width: 150px;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.btn-download {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-download:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-delete {
  background: #fee2e2;
  color: #991b1b;
}

.btn-delete:hover:not(:disabled) {
  background: #fecaca;
}

.btn-download:disabled,
.btn-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.btn-pagination {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-pagination:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-pagination:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: #64748b;
  font-weight: 600;
}
</style>
