<template>
  <footer class="footer">
    <div class="container footer-content">
      <div>
        <p class="footer-brand">Expert Polymer</p>
        <p>Анализ структуры композитных материалов.</p>
        <p>© {{ new Date().getFullYear() }} Expert Polymer</p>
      </div>
      <nav aria-label="Дополнительная навигация">
        <RouterLink to="/about">О системе</RouterLink
        ><RouterLink to="/contacts">Контакты</RouterLink
        ><RouterLink to="/settings">Настройки</RouterLink
        ><RouterLink to="/usage">Использование и данные</RouterLink>
      </nav>
      <div>
        <a href="mailto:info@expertpolymer.ru">info@expertpolymer.ru</a>
        <p>Казань, ул. Петербургская, 52</p>
      </div>
    </div>
  </footer>
</template>
<style scoped>
.footer {
  background: var(--nav-gradient);
  color: #e3edfb;
  padding: 2.5rem 0;
  margin-top: auto;
}
.footer-content {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 2rem;
}
.footer-brand {
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
}
nav {
  display: flex;
  flex-direction: column;
  align-items: start;
  gap: 0.6rem;
}
a,
a:hover {
  color: white;
}
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>
