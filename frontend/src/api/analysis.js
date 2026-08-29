import { apiFetch } from './client'
import { getAuthToken, getCurrentUser } from './auth'

/**
 * Синхронная загрузка и анализ изображения
 * @param {File} file - Файл изображения
 * @param {string} token - JWT токен (опционально)
 * @returns {Promise<Object>} Результат анализа
 */
export async function analyzeImage(file, token = getAuthToken()) {
  if (!token) {
    throw new Error('Требуется авторизация для анализа изображения')
  }

  const formData = new FormData()
  formData.append('file', file)

  return apiFetch('/api/analyze', {
    method: 'POST',
    token,
    body: formData,
  })
}

/**
 * Асинхронная загрузка и анализ изображения (через Celery)
 * @param {File} file - Файл изображения
 * @param {string} token - JWT токен (опционально)
 * @returns {Promise<Object>} Объект с task_id для отслеживания
 */
export async function analyzeImageAsync(file, token = getAuthToken()) {
  if (!token) {
    throw new Error('Требуется авторизация для анализа изображения')
  }

  const formData = new FormData()
  formData.append('file', file)

  return apiFetch('/api/analyze/async', {
    method: 'POST',
    token,
    body: formData,
  })
}

/**
 * Получить статус фоновой задачи анализа
 * @param {string} taskId - ID задачи из Celery
 * @param {string} token - JWT токен (опционально)
 * @returns {Promise<Object>} Статус задачи
 */
export async function getAnalysisTaskStatus(taskId, token = getAuthToken()) {
  if (!token) {
    throw new Error('Требуется авторизация')
  }

  return apiFetch(`/api/analyze/tasks/${taskId}`, { token })
}

/**
 * Получить результаты анализа по ID
 * @param {number} resultId - ID результата анализа
 * @param {string} token - JWT токен (опционально)
 * @returns {Promise<Object>} Результат анализа
 */
export async function getAnalysisResult(resultId, token = getAuthToken()) {
  if (!token) {
    throw new Error('Требуется авторизация')
  }

  return apiFetch(`/api/results/${resultId}`, { token })
}

/**
 * Получить историю всех анализов пользователя
 * @param {Object} params - Параметры фильтрации
 * @param {number} params.userId - ID пользователя (для admin/director)
 * @param {string} params.date - Дата анализа (формат YYYY-MM-DD)
 * @param {number} params.limit - Количество результатов (по умолчанию 20)
 * @param {number} params.offset - Сдвиг для пагинации (по умолчанию 0)
 * @param {string} token - JWT токен (опционально)
 * @returns {Promise<Array>} Список результатов анализа
 */
export async function getAnalysisHistory(params = {}, token = getAuthToken()) {
  if (!token) {
    throw new Error('Требуется авторизация')
  }

  const search = new URLSearchParams()

  if (params.userId != null) search.set('user_id', String(params.userId))
  if (params.date) search.set('date', params.date)
  if (params.limit != null) search.set('limit', String(params.limit || 20))
  if (params.offset != null) search.set('offset', String(params.offset || 0))

  const query = search.toString()
  const path = query ? `/api/history?${query}` : '/history'

  return apiFetch(path, { token })
}

/**
 * Удалить результат анализа
 * @param {number} resultId - ID результата анализа
 * @param {string} token - JWT токен (опционально)
 * @returns {Promise<Object>} Ответ сервера
 */
export async function deleteAnalysisResult(resultId, token = getAuthToken()) {
  if (!token) {
    throw new Error('Требуется авторизация')
  }

  return apiFetch(`/api/results/${resultId}`, {
    method: 'DELETE',
    token,
  })
}

/**
 * Загрузить результат анализа в виде отчета (JSON)
 * @param {number} resultId - ID результата анализа
 * @param {string} token - JWT токен (опционально)
 * @returns {Promise<Blob>} Файл отчета
 */
export async function downloadAnalysisReport(resultId, token = getAuthToken()) {
  if (!token) {
    throw new Error('Требуется авторизация')
  }

  try {
    const result = await getAnalysisResult(resultId, token)

    const reportData = {
      id: result.id,
      filename: result.original_filename,
      result: result.result,
      confidence: result.confidence,
      width: result.width,
      height: result.height,
      created_at: result.created_at,
      result_data: result.result_data,
    }

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    return blob
  } catch (error) {
    throw new Error(`Ошибка загрузки отчета: ${error.message}`)
  }
}
