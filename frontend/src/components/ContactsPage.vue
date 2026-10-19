<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import FormField from './ui/FormField.vue'
import { contactBody, contactMailto } from '@/utils/contact'
import { saveBlob } from '@/utils/files'
const form = reactive({ name: '', email: '', subject: '', message: '' })
const prepared = ref(false)
const notice = ref('')
const mailto = computed(() => contactMailto(form))
function resetPreparation() {
  prepared.value = false
  notice.value = ''
}
function prepare() {
  prepared.value = true
  notice.value = ''
}
function download() {
  try {
    saveBlob(
      new Blob([form.subject + '\n\n' + contactBody(form)], { type: 'text/plain;charset=utf-8' }),
      'expert-polymer-message.txt',
    )
    notice.value =
      'Черновик сохранён. Отправьте его на info@expertpolymer.ru из своей почтовой программы.'
  } catch {
    notice.value = 'Не удалось сохранить черновик. Скопируйте текст из формы.'
  }
}
</script>
<template>
  <div class="page-shell">
    <header class="page-heading">
      <h1>Контакты</h1>
      <p>Вопросы об анализе материалов, работе системы и сотрудничестве.</p>
    </header>
    <div class="contacts-grid">
      <section class="panel">
        <h2>Связаться с нами</h2>
        <dl class="contact-details">
          <dt>Адрес</dt>
          <dd>Казань, ул. Петербургская, 52, ИТ-Парк</dd>
          <dt>Телефон</dt>
          <dd><a href="tel:+79373689693">+7 (937) 368-96-93</a></dd>
          <dt>Email</dt>
          <dd><a href="mailto:info@expertpolymer.ru">info@expertpolymer.ru</a></dd>
          <dt>Поддержка</dt>
          <dd><a href="mailto:support@expertpolymer.ru">support@expertpolymer.ru</a></dd>
          <dt>Время работы</dt>
          <dd>Пн–Пт, 9:00–18:00, московское время</dd>
        </dl>
        <a
          class="btn btn-secondary"
          href="https://yandex.ru/maps/?text=Казань%2C%20Петербургская%2052"
          target="_blank"
          rel="noopener noreferrer"
          >Открыть адрес в картах</a
        >
      </section>
      <form class="panel form-stack" @submit.prevent="prepare" @input="resetPreparation">
        <h2>Подготовить письмо</h2>
        <p class="muted">
          Форма подготовит письмо для вашей почтовой программы. Сайт не отправляет сообщения
          автоматически.
        </p>
        <FormField
          v-model="form.name"
          label="Ваше имя"
          autocomplete="name"
          required
          minlength="2"
          maxlength="100"
          pattern=".*\S.*"
        />
        <FormField
          v-model="form.email"
          label="Email для ответа"
          type="email"
          autocomplete="email"
          required
          maxlength="254"
        />
        <FormField
          v-model="form.subject"
          label="Тема"
          required
          minlength="2"
          maxlength="150"
          pattern=".*\S.*"
        />
        <div class="form-field">
          <label for="contact-message">Сообщение</label
          ><textarea
            id="contact-message"
            v-model="form.message"
            required
            minlength="10"
            maxlength="2000"
            rows="6"
          />
        </div>
        <button class="btn btn-primary" type="submit">Подготовить письмо</button>
        <div v-if="prepared" class="notice" role="status">
          <p>Письмо подготовлено. Откройте почтовую программу и подтвердите отправку в ней.</p>
          <div class="actions">
            <a class="btn btn-primary" :href="mailto">Открыть почтовую программу</a
            ><button type="button" class="btn btn-secondary" @click="download">
              Скачать черновик
            </button>
          </div>
        </div>
        <p v-if="notice" role="status">{{ notice }}</p>
      </form>
    </div>
  </div>
</template>
<style scoped>
.contacts-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr);
  gap: 1.5rem;
  align-items: start;
}
.contact-details {
  margin: 0 0 1.5rem;
}
dt {
  font-weight: 650;
}
dd {
  margin: 0.25rem 0 1rem;
  overflow-wrap: anywhere;
}
@media (max-width: 760px) {
  .contacts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
