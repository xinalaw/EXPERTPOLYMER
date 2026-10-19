<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, useId, watch } from 'vue'
const props = defineProps<{ open: boolean; title: string; busy?: boolean }>()
const emit = defineEmits<{ close: [] }>()
const dialog = ref<HTMLDialogElement | null>(null)
const titleId = useId()
let previousFocus: HTMLElement | null = null
let previousOverflow = ''
let locked = false
function unlock() {
  if (!locked) return
  document.body.style.overflow = previousOverflow
  locked = false
  if (previousFocus?.isConnected) previousFocus.focus()
}
watch(
  () => props.open,
  async (open) => {
    await nextTick()
    if (open && !dialog.value?.open) {
      previousFocus = document.activeElement as HTMLElement
      previousOverflow = document.body.style.overflow
      locked = true
      document.body.style.overflow = 'hidden'
      dialog.value?.showModal()
    } else if (!open) {
      dialog.value?.close()
      unlock()
    }
  },
  { immediate: true },
)
function close() {
  if (!props.busy) emit('close')
}
onBeforeUnmount(unlock)
</script>
<template>
  <Teleport to="body">
    <dialog
      ref="dialog"
      class="app-dialog"
      :aria-labelledby="titleId"
      aria-modal="true"
      @cancel.prevent="close"
      @click="$event.target === dialog && close()"
      @close="unlock"
    >
      <div class="dialog-body" :aria-busy="busy">
        <header class="dialog-heading">
          <h2 :id="titleId">{{ title }}</h2>
          <button
            class="icon-button"
            type="button"
            aria-label="Закрыть окно"
            :disabled="busy"
            @click="close"
          >
            ×
          </button>
        </header>
        <slot />
      </div>
    </dialog>
  </Teleport>
</template>
<style scoped>
.app-dialog {
  position: fixed;
  inset: 0;
  margin: auto;
  padding: 0;
  border: 0;
  border-radius: var(--radius);
  width: min(520px, calc(100% - 2rem));
  max-height: calc(100dvh - 2rem);
  color: var(--text);
  box-shadow: var(--shadow);
}
.app-dialog::backdrop {
  background: rgb(15 23 42 / 65%);
}
.dialog-body {
  padding: 1.5rem;
}
.dialog-heading {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  align-items: start;
}
.dialog-heading h2 {
  font-size: 1.4rem;
}
</style>
