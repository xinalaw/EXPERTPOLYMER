<template>
  <footer class="footer">
    <div class="container footer-content">
      <div>
        <p class="footer-brand">Expert Polymer</p>
        <p>Анализ структуры композитных материалов.</p>
        <p>© {{ new Date().getFullYear() }} Expert Polymer</p>
      </div>
      <div class="footer-support">
        <img
          class="footer-support-logo"
          src="/logo.jpg"
          alt="Фонд содействия инновациям"
          width="1366"
          height="828"
          loading="lazy"
        />
        <p>Проект разработан при поддержке Фонда содействия инновациям (ФСИ).</p>
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
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 2rem;
}
.footer-brand {
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
}
.footer-support {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}
.footer-support-logo {
  display: block;
  width: 180px;
  max-width: 100%;
  height: auto;
  flex-shrink: 0;
  border-radius: 8px;
}
.footer-support p {
  margin: 0;
}
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
@media (max-width: 480px) {
  .footer-support {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
