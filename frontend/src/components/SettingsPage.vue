<script setup lang="ts">
import { reactive, ref } from 'vue'
import { preferences, updatePreferences } from '@/stores/preferences'
const form = reactive({ ...preferences })
const message = ref('')
function save() {
  message.value = updatePreferences(form)
    ? 'Настройки сохранены на этом устройстве.'
    : 'Настройки применены до закрытия страницы: браузер не разрешает их сохранить.'
}
</script>
<template>
  <div class="page-shell narrow">
    <header class="page-heading">
      <h1>Настройки</h1>
      <p>Параметры отображения на этом устройстве.</p>
    </header>
    <form class="panel form-stack" @submit.prevent="save">
      <label class="checkbox-row"
        ><input v-model="form.reducedMotion" type="checkbox" /> Уменьшить анимацию</label
      >
      <p class="muted">Системная настройка уменьшения движения учитывается автоматически.</p>
      <div class="form-field">
        <label for="page-size">Анализов на странице истории</label
        ><select id="page-size" v-model.number="form.pageSize">
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </div>
      <button class="btn btn-primary" type="submit">Сохранить настройки</button>
      <p v-if="message" role="status">{{ message }}</p>
    </form>
  </div>
</template>
