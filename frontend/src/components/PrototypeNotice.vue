<template>
  <aside class="prototype-notice" aria-label="Ограничения прототипа">
    <div class="page-shell">
      <strong>Прототип · демонстрационная версия</strong>
      <p>Модель может ошибаться. Результаты анализа требуют проверки специалистом.</p>
      <p>
        Для демонстрации используйте синтетические СЭМ-снимки частиц из
        <RouterLink to="/generation">генератора изображений</RouterLink>. Работа с произвольными
        изображениями не гарантируется.
      </p>
    </div>
  </aside>
</template>
<style scoped>
.prototype-notice {
  background: #fff4d6;
  color: #533c0c;
  border-bottom: 1px solid #d5b662;
}
.prototype-notice .page-shell {
  padding-top: 1rem;
  padding-bottom: 1rem;
}
p {
  margin: 0.35rem 0 0;
}
a {
  color: #624400;
  text-decoration: underline;
}
</style>
