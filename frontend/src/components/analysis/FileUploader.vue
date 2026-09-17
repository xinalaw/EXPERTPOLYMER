<script setup lang="ts">
import { ref } from 'vue'
import { IMAGE_ACCEPT } from '@/utils/files'
const props = defineProps<{ busy: boolean }>()
const emit = defineEmits<{ select: [file: File]; invalid: [message: string] }>()
const input = ref<HTMLInputElement | null>(null)
const dragging = ref(false)
function drop(event: DragEvent) {
  dragging.value = false
  if (!props.busy) select(event.dataTransfer?.files || null)
}
function select(files: FileList | null) {
  if (!files?.length) return
  if (files.length !== 1) {
    emit('invalid', 'Выберите одно изображение для анализа.')
    return
  }
  emit('select', files[0]!)
}
function change(event: Event) {
  const target = event.target as HTMLInputElement
  select(target.files)
  target.value = ''
}
</script>
<template>
  <div
    class="upload-area"
    :class="{ dragging }"
    @dragover.prevent="dragging = true"
    @dragleave.self="dragging = false"
    @drop.prevent="drop"
  >
    <h2>Загрузите изображение</h2>
    <p>Перетащите один файл сюда или выберите его на устройстве.</p>
    <p id="upload-hint" class="muted">
      JPG, PNG, TIFF, BMP · до 20 МБ. Предпросмотр TIFF зависит от браузера.
    </p>
    <input ref="input" type="file" :accept="IMAGE_ACCEPT" hidden @change="change" />
    <button
      class="btn btn-primary"
      :disabled="busy"
      aria-describedby="upload-hint"
      @click="input?.click()"
    >
      {{ busy ? 'Проверка файла…' : 'Выбрать файл' }}
    </button>
  </div>
</template>
<style scoped>
.upload-area {
  padding: clamp(1.5rem, 6vw, 4rem);
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  text-align: center;
  background: var(--surface);
}
.dragging {
  border-color: var(--primary);
  background: var(--surface-muted);
}
</style>
