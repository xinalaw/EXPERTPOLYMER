<script setup lang="ts">
import { useId } from 'vue'
defineOptions({ inheritAttrs: false })
defineProps<{ label: string; error?: string; hint?: string; type?: string }>()
const model = defineModel<string>({ default: '' })
const id = useId()
</script>
<template>
  <div class="form-field">
    <label :for="id">{{ label }}</label>
    <input
      :id="id"
      v-model="model"
      :type="type || 'text'"
      v-bind="$attrs"
      :aria-invalid="!!error"
      :aria-describedby="error ? id + '-error' : hint ? id + '-hint' : undefined"
    />
    <p v-if="hint" :id="id + '-hint'" class="field-hint">{{ hint }}</p>
    <p v-if="error" :id="id + '-error'" class="field-error">{{ error }}</p>
  </div>
</template>
