import { File as NodeFile } from 'node:buffer'
import { describe, expect, it, vi } from 'vitest'
import { downloadReport, formatPercent, MAX_FILE_SIZE, validateImage } from './files'
import { contactBody, contactMailto } from './contact'
import type { AnalysisResult } from '@/api/types'

const png = [137, 80, 78, 71, 13, 10, 26, 10]
function file(bytes: number[], name = 'sample.png', type = 'image/png') {
  return new NodeFile([new Uint8Array(bytes)], name, { type }) as unknown as File
}
describe('image validation', () => {
  it('accepts matching signatures, including a missing browser MIME', async () => {
    expect(await validateImage(file(png))).toBe('')
    expect(await validateImage(file([73, 73, 42, 0], 'sample.tif', ''))).toBe('')
  })
  it('rejects disguised files and unsupported images', async () => {
    expect(await validateImage(file([60, 115, 118, 103]))).toContain('не соответствует')
    expect(await validateImage(file(png, 'sample.svg', 'image/svg+xml'))).toContain('JPG')
    expect(await validateImage(file(png, 'sample.png', 'text/html'))).toContain('JPG')
  })
  it('rejects empty and oversized files before reading them', async () => {
    expect(await validateImage(file([]))).toContain('пуст')
    const oversized = file(png)
    Object.defineProperty(oversized, 'size', { value: MAX_FILE_SIZE + 1 })
    expect(await validateImage(oversized)).toContain('20 МБ')
  })
})
it('downloads the report and releases the object URL', () => {
  vi.useFakeTimers()
  const createObjectURL = vi.fn().mockReturnValue('blob:report')
  const revokeObjectURL = vi.fn()
  vi.stubGlobal('URL', Object.assign(class extends URL {}, { createObjectURL, revokeObjectURL }))
  const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
  const result: AnalysisResult = {
    id: 7,
    user_id: 1,
    original_filename: 'sample.png',
    result: 'ok',
    created_at: '2026-09-10T12:00:00Z',
    result_data: { particles_detected: 0 },
  }
  downloadReport(result)
  expect(click).toHaveBeenCalledOnce()
  expect(createObjectURL.mock.calls[0]![0].type).toBe('application/json')
  expect(document.querySelector('a[download]')).toBeNull()
  vi.runAllTimers()
  expect(revokeObjectURL).toHaveBeenCalledWith('blob:report')
})
it('does not report missing confidence as zero', () => {
  expect(formatPercent(undefined)).toBe('—')
  expect(formatPercent(0)).toBe('0%')
  expect(formatPercent(Number.NaN)).toBe('—')
})
it('prepares an encoded draft without silently adding recipients or losing user text', () => {
  const draft = {
    name: 'Анна',
    email: 'anna@example.com',
    subject: 'Вопрос &bcc=other@example.com',
    message: 'Текст\nс новой строкой',
  }
  const url = new URL(contactMailto(draft))
  expect(url.searchParams.has('bcc')).toBe(false)
  expect(url.searchParams.get('subject')).toBe(draft.subject)
  expect(url.searchParams.get('body')).toBe(contactBody(draft))
})
