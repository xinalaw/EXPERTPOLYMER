import { apiFetch } from './client'
import type { AnalysisResult } from './types'

export function analyzeImage(file: File, signal?: AbortSignal) {
  const body = new FormData()
  const extension = file.name.split('.').pop()?.toLowerCase() || ''
  const mime: Record<string, string> = {
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    tif: 'image/tiff',
    tiff: 'image/tiff',
    bmp: 'image/bmp',
  }
  body.append('file', file.type ? file : new Blob([file], { type: mime[extension] }), file.name)
  return apiFetch<AnalysisResult>('/api/analyze', {
    method: 'POST',
    body,
    signal,
    timeoutMs: 180000,
  })
}

export function getAnalysisResult(id: number, signal?: AbortSignal) {
  return apiFetch<AnalysisResult>(`/api/results/${id}`, { signal })
}

export function getAnalysisHistory(
  params: { limit?: number; offset?: number; date?: string } = {},
  signal?: AbortSignal,
) {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') query.set(key, String(value))
  }
  return apiFetch<AnalysisResult[]>(`/api/history${query.size ? `?${query}` : ''}`, { signal })
}

export function deleteAnalysisResult(id: number) {
  return apiFetch(`/api/results/${id}`, { method: 'DELETE' })
}
