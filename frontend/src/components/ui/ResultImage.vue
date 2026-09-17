<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps<{ src?: string; alt: string }>()
const failed = ref(false)
watch(
  () => props.src,
  () => {
    failed.value = false
  },
)
</script>
<template>
  <figure class="result-picture">
    <img
      v-if="src && !failed"
      :src="src"
      :alt="alt"
      loading="lazy"
      decoding="async"
      @error="failed = true"
    />
    <p v-else class="muted">Предпросмотр недоступен. Данные анализа и отчёт доступны отдельно.</p>
    <figcaption>{{ alt }}</figcaption>
  </figure>
</template>
<style scoped>
.result-picture {
  min-width: 0;
}
img {
  display: block;
  width: 100%;
  height: 280px;
  object-fit: contain;
  border-radius: var(--radius);
  background: var(--surface-muted);
}
figcaption {
  font-size: 0.9rem;
  color: var(--muted);
  margin-top: 0.5rem;
}
</style>
