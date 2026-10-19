import { afterEach, vi } from 'vitest'
import { enableAutoUnmount } from '@vue/test-utils'

enableAutoUnmount(afterEach)
// jsdom has no native dialog implementation; real focus trapping is covered in Playwright.
if (!HTMLDialogElement.prototype.showModal) {
  HTMLDialogElement.prototype.showModal = function () {
    this.open = true
  }
  HTMLDialogElement.prototype.close = function () {
    this.open = false
  }
}
afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})
