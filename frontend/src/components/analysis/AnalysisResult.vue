<script setup lang="ts">
import { computed } from 'vue'
import type { AnalysisResult } from '@/api/types'
import { staticUrl } from '@/api/client'
import { formatPercent } from '@/utils/files'
import ResultImage from '@/components/ui/ResultImage.vue'
const props = defineProps<{ result: AnalysisResult; original?: string }>()
const data = computed(() => props.result.result_data)
const expert = computed(() => data.value?.expert)
const conclusion = computed(() =>
  (props.result.result || '').replace(/\s*Оценка пригодности [\s\S]*$/, '').trim(),
)
const labels: Record<string, string> = {
  dendritic: 'Дендритные',
  fragmented: 'Осколочные',
  spongy: 'Губчатые',
  spherical: 'Сферические',
  teardrop: 'Каплевидные',
}
const verdicts: Record<string, string> = {
  suitable: 'Пригоден',
  conditional: 'Условно пригоден',
  unsuitable: 'Не пригоден',
}
const composition = computed(() =>
  Object.entries(data.value?.composition || {})
    .filter(([, value]) => Number.isFinite(value) && value > 0)
    .map(([name, value]) => ({ name: labels[name] || name, value: Math.min(100, value) }))
    .sort((a, b) => b.value - a.value),
)
</script>
<template>
  <div class="result-details">
    <div class="image-pair">
      <ResultImage :src="original || staticUrl(result.image_path)" alt="Исходное изображение" />
      <ResultImage :src="staticUrl(result.processed_image_path)" alt="Обработанное изображение" />
    </div>
    <dl class="metrics">
      <div>
        <dt>Результат</dt>
        <dd>{{ conclusion || '—' }}</dd>
      </div>
      <div>
        <dt>Уверенность</dt>
        <dd>{{ formatPercent(result.confidence) }}</dd>
      </div>
      <div>
        <dt>Частиц обнаружено</dt>
        <dd>{{ data?.particles_detected ?? '—' }}</dd>
      </div>
      <div>
        <dt>Размер изображения</dt>
        <dd>{{ result.width ?? '—' }} × {{ result.height ?? '—' }} px</dd>
      </div>
    </dl>
    <section v-if="expert" class="expert-panel">
      <h3>Заключение экспертной системы</h3>
      <p class="verdict">
        {{ verdicts[expert.verdict || ''] || expert.verdict || 'Оценка' }} ·
        {{ expert.score ?? '—' }}/100
      </p>
      <p>{{ expert.conclusion }}</p>
      <dl v-if="expert.inputs" class="metrics">
        <div>
          <dt>Сферичность</dt>
          <dd>{{ formatPercent(expert.inputs.sphericity) }}</dd>
        </div>
        <div>
          <dt>Округлость</dt>
          <dd>{{ formatPercent(expert.inputs.smoothness) }}</dd>
        </div>
        <div>
          <dt>Однородность размеров</dt>
          <dd>{{ formatPercent(expert.inputs.uniformity) }}</dd>
        </div>
      </dl>
    </section>
    <p v-else class="notice">Для этого анализа экспертная оценка не предоставлена.</p>
    <section v-if="composition.length">
      <h3>Состав порошка</h3>
      <div v-for="item in composition" :key="item.name" class="composition-row">
        <span>{{ item.name }}</span
        ><meter min="0" max="100" :value="item.value" :aria-label="item.name" /><span
          >{{ item.value }}%</span
        >
      </div>
    </section>
    <section v-if="data?.avg_circularity != null || data?.size_stats">
      <h3>Морфология</h3>
      <dl class="metrics">
        <div>
          <dt>Средняя округлость</dt>
          <dd>{{ data.avg_circularity ?? '—' }}</dd>
        </div>
        <div>
          <dt>Дисперсность</dt>
          <dd>{{ data.dispersity ?? '—' }}</dd>
        </div>
        <div v-if="data.size_stats">
          <dt>Диаметр частиц, px</dt>
          <dd>{{ data.size_stats.min_px ?? '—' }} – {{ data.size_stats.max_px ?? '—' }}</dd>
        </div>
        <div v-if="data.size_stats">
          <dt>Средний диаметр, px</dt>
          <dd>{{ data.size_stats.mean_px ?? '—' }} ± {{ data.size_stats.std_px ?? '—' }}</dd>
        </div>
      </dl>
    </section>
    <section v-if="data?.model">
      <h3>Модель анализа</h3>
      <p>
        {{ data.model.name || '—' }} · {{ data.model.version || '—' }} ·
        {{ data.model.type || '—' }}
      </p>
      <p v-if="data.processing_time_ms != null" class="muted">
        Время обработки: {{ Math.round(data.processing_time_ms) }} мс
      </p>
    </section>
    <details v-if="data?.detections?.length">
      <summary>Обнаруженные объекты: {{ data.detections.length }}</summary>
      <ul class="detection-list">
        <li v-for="(detection, index) in data.detections.slice(0, 100)" :key="index">
          {{ detection.label || 'Объект' }} — {{ formatPercent(detection.confidence) }}
        </li>
      </ul>
      <p v-if="data.detections.length > 100" class="muted">
        Показаны первые 100 объектов. Полный список — в JSON-отчёте.
      </p>
    </details>
  </div>
</template>
<style scoped>
.result-details {
  display: grid;
  gap: 1.5rem;
}
.image-pair {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
.expert-panel {
  background: var(--surface-muted);
  padding: 1.5rem;
  border-radius: var(--radius);
}
.verdict {
  font-size: 1.2rem;
  font-weight: 700;
}
.composition-row {
  display: grid;
  grid-template-columns: 1fr 2fr auto;
  gap: 1rem;
  align-items: center;
  margin: 0.5rem 0;
}
meter {
  width: 100%;
}
.detection-list {
  max-height: 20rem;
  overflow: auto;
  padding-left: 1.5rem;
}
@media (max-width: 600px) {
  .image-pair {
    grid-template-columns: 1fr;
  }
  .composition-row {
    gap: 0.5rem;
  }
}
</style>
