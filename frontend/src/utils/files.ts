import type { AnalysisResult } from '@/api/types'

export const MAX_FILE_SIZE = 20 * 1024 * 1024
export const IMAGE_ACCEPT = '.jpg,.jpeg,.png,.tif,.tiff,.bmp'
const types: Record<string, string[]> = {
  jpg: ['image/jpeg'],
  jpeg: ['image/jpeg'],
  png: ['image/png'],
  tif: ['image/tiff', 'image/x-tiff'],
  tiff: ['image/tiff', 'image/x-tiff'],
  bmp: ['image/bmp', 'image/x-ms-bmp', 'image/x-bmp'],
}

export async function validateImage(file: File): Promise<string> {
  const ext = file.name.split('.').pop()?.toLowerCase() || ''
  if (!types[ext] || (file.type && !types[ext].includes(file.type)))
    return 'Выберите изображение JPG, PNG, TIFF или BMP.'
  if (!file.size) return 'Файл пуст. Выберите другое изображение.'
  if (file.size > MAX_FILE_SIZE) return 'Размер файла не должен превышать 20 МБ.'
  const bytes = new Uint8Array(await file.slice(0, 8).arrayBuffer())
  const matches = (signature: number[]) => signature.every((byte, index) => bytes[index] === byte)
  const valid =
    ext === 'png'
      ? matches([137, 80, 78, 71, 13, 10, 26, 10])
      : ['jpg', 'jpeg'].includes(ext)
        ? matches([255, 216, 255])
        : ext === 'bmp'
          ? matches([66, 77])
          : matches([73, 73, 42, 0]) || matches([77, 77, 0, 42])
  return valid ? '' : 'Содержимое файла не соответствует формату изображения.'
}

export function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  try {
    link.click()
  } finally {
    link.remove()
    // Keep the URL alive long enough for the browser to start reading the download.
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
}

export function downloadReport(result: AnalysisResult) {
  const {
    id,
    original_filename,
    result: verdict,
    confidence,
    width,
    height,
    created_at,
    result_data,
  } = result
  const report = {
    id,
    filename: original_filename,
    result: verdict,
    confidence,
    width,
    height,
    created_at,
    result_data,
  }
  saveBlob(
    new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }),
    `analysis-report-${id}.json`,
  )
}

export function formatPercent(value?: number | null) {
  return typeof value === 'number' && Number.isFinite(value)
    ? `${Math.round(Math.max(0, Math.min(1, value)) * 100)}%`
    : '—'
}

export function formatDate(value: string) {
  // The backend currently serializes naive UTC datetimes.
  const date = new Date(/(?:Z|[+-]\d{2}:\d{2})$/i.test(value) ? value : `${value}Z`)
  return Number.isNaN(date.getTime())
    ? 'Дата неизвестна'
    : date.toLocaleString('ru-RU', { dateStyle: 'medium', timeStyle: 'short' })
}
