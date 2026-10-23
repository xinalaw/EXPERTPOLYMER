<script setup lang="ts">
defineProps<{ page: number; hasNext: boolean; loading: boolean }>()
const emit = defineEmits<{ change: [page: number] }>()
</script>
<template>
  <nav class="admin-pagination" aria-label="Страницы списка">
    <button
      class="btn btn-secondary"
      :disabled="loading || page === 1"
      @click="emit('change', page - 1)"
    >
      Назад
    </button>
    <span aria-live="polite">Страница {{ page }}</span>
    <button
      class="btn btn-secondary"
      :disabled="loading || !hasNext"
      @click="emit('change', page + 1)"
    >
      Далее
    </button>
  </nav>
</template>
