<script setup lang="ts">
defineProps<{ items: { title: string; text: string; symbol: string }[] }>()
</script>
<template>
  <div class="feature-grid">
    <article v-for="item in items" :key="item.title" class="panel feature-card">
      <span class="feature-symbol" aria-hidden="true">{{ item.symbol }}</span>
      <h3>{{ item.title }}</h3>
      <p>{{ item.text }}</p>
    </article>
  </div>
</template>
<style scoped>
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(240px, 100%), 1fr));
  gap: 1.25rem;
}
.feature-card {
  margin: 0;
}
.feature-symbol {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  width: 48px;
  height: 48px;
  margin-bottom: 1.25rem;
  color: white;
  background: var(--brand-gradient);
  font-size: 1.6rem;
}
.feature-card p {
  color: var(--muted);
}
</style>
