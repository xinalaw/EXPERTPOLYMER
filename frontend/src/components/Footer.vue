<template>
  <footer class="footer">
    <div class="container footer-content">
      <div class="footer-info">
        <p class="footer-brand">Expert Polymer</p>
        <p>Анализ структуры композитных материалов.</p>
        <p class="footer-copyright">© {{ new Date().getFullYear() }} Expert Polymer</p>
      </div>
      <div class="footer-support">
        <div class="footer-support-logos">
          <img
            class="footer-support-logo"
            src="/logo.jpg"
            alt="Фонд содействия инновациям"
            width="1366"
            height="828"
            loading="lazy"
          />
          <img
            class="footer-support-logo"
            src="/logo2.png"
            alt="Платформа университетского технологического предпринимательства"
            width="2535"
            height="1976"
            loading="lazy"
          />
        </div>
        <p>
          Проект реализован при поддержке Фонда содействия инновациям в рамках программы
          «Студенческий стартап» мероприятия «Платформа университетского технологического
          предпринимательства» федерального проекта «Технологии»
        </p>
      </div>
    </div>
  </footer>
</template>
<style scoped>
.footer {
  background: var(--nav-gradient);
  color: #e3edfb;
  padding: clamp(2rem, 4vw, 3rem) 0;
  margin-top: auto;
}
.footer-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 2.5fr);
  align-items: start;
  gap: clamp(2rem, 5vw, 5rem);
}
.footer-info p {
  margin: 0;
}
.footer-info > p + p {
  margin-top: 0.75rem;
}
.footer-info > .footer-copyright {
  margin-top: 1.75rem;
  font-size: 0.85rem;
  color: #b7c9e2;
}
.footer-brand {
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
}
.footer-support {
  display: grid;
  grid-template-columns: minmax(0, 260px) minmax(0, 1fr);
  align-items: center;
  gap: 1rem;
}
.footer-support-logos {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: center;
  width: min(100%, 340px);
  padding: 0.5rem;
  background: white;
  border: 1px solid #e3e9f2;
  border-radius: 12px;
  overflow: hidden;
}
.footer-support-logo {
  display: block;
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  height: clamp(72px, 8vw, 92px);
  object-fit: contain;
  padding-inline: 0.5rem;
}
.footer-support-logo + .footer-support-logo {
  border-left: 1px solid #e3e9f2;
}
.footer-support p {
  margin: 0;
  max-width: 65ch;
  font-size: 0.9rem;
  line-height: 1.7;
  text-wrap: pretty;
}
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 1.75rem;
  }
  .footer-support {
    padding-top: 1.75rem;
    border-top: 1px solid rgb(255 255 255 / 16%);
  }
}
@media (max-width: 540px) {
  .footer-support {
    grid-template-columns: 1fr;
  }
}
</style>
