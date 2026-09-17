import { flushPromises, mount } from '@vue/test-utils'
import { expect, it, vi } from 'vitest'
import AppDialog from './AppDialog.vue'
import FormField from './FormField.vue'
import AnalysisResult from '../analysis/AnalysisResult.vue'

it('labels fields and associates errors', () => {
  const first = mount(FormField, { props: { label: 'Email', error: 'Неверный email' } })
  const second = mount(FormField, { props: { label: 'Email' } })
  expect(first.find('label').attributes('for')).toBe(first.find('input').attributes('id'))
  expect(first.find('input').attributes('aria-describedby')).toBe(
    first.find('.field-error').attributes('id'),
  )
  expect(first.find('input').attributes('aria-invalid')).toBe('true')
  // Separate Vue apps have independent useId prefixes; uniqueness within an app is tested by the browser suite.
  expect(second.find('input').attributes('aria-invalid')).toBe('false')
})
it('opens a native modal, handles Escape, locks scroll and restores focus', async () => {
  const show = vi.spyOn(HTMLDialogElement.prototype, 'showModal').mockImplementation(function (
    this: HTMLDialogElement,
  ) {
    this.open = true
  })
  vi.spyOn(HTMLDialogElement.prototype, 'close').mockImplementation(function (
    this: HTMLDialogElement,
  ) {
    this.open = false
  })
  const trigger = document.createElement('button')
  document.body.append(trigger)
  trigger.focus()
  const wrapper = mount(AppDialog, {
    props: { open: true, title: 'Удалить?' },
    attachTo: document.body,
  })
  await flushPromises()
  expect(show).toHaveBeenCalledOnce()
  expect(document.body.style.overflow).toBe('hidden')
  document.querySelector('dialog')!.dispatchEvent(new Event('cancel', { cancelable: true }))
  expect(wrapper.emitted('close')).toHaveLength(1)
  await wrapper.setProps({ open: false })
  await flushPromises()
  expect(document.activeElement).toBe(trigger)
  expect(document.body.style.overflow).toBe('')
  trigger.remove()
})
it('renders partial expert data without throwing or showing fabricated confidence', () => {
  const wrapper = mount(AnalysisResult, {
    props: {
      result: {
        id: 1,
        user_id: 1,
        original_filename: 'a.tif',
        result: 'ok',
        created_at: '',
        result_data: { expert: { verdict: 'conditional' } },
      },
    },
  })
  expect(wrapper.text()).toContain('Условно пригоден')
  expect(wrapper.text()).not.toContain('NaN')
  expect(wrapper.text()).not.toContain('undefined')
})
