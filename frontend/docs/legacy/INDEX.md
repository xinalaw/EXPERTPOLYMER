# 📚 ПОЛНЫЙ УКАЗАТЕЛЬ ДОКУМЕНТАЦИИ

## 🎯 ЕСЛИ ВЫ В СПЕШКЕ (2 минуты)

**Выполните по порядку:**
1. Отредактируйте `.env` - параметры вашей БД
2. Выполните SQL из `query.sql` в PostgreSQL
3. Запустите: `npm run api`
4. В новом терминале: `npm run dev`
5. Откройте: `http://localhost:5173/`

→ Полная инструкция: **QUICKSTART.md**

---

## 📖 ПОЛНАЯ ДОКУМЕНТАЦИЯ

### `QUICKSTART.md` ⭐ НАЧНИТЕ ОТСЮДА
**Пошаговая инструкция в 4 шага**
- Как обновить `.env`
- Как создать таблицу в PostgreSQL
- Как запустить сервер и фронт
- Как тестировать

### `AUTH_SETUP.md`
**Подробная техническая документация**
- Описание всех 4 API endpoints
- Примеры запросов и ответов
- Объяснение каждого параметра
- Инструкции по безопасности

### `IMPLEMENTATION_SUMMARY.md`
**Что было сделано и как это работает**
- ✅ Краткое резюме всех изменений
- 🚀 Пошаговый старт системы
- 📡 Все API endpoints с примерами
- 💾 Как работает сохранение сессии

### `TESTING.md`
**Диагностика и проверка работы**
- ✅ Чек-лист перед запуском
- 🧪 Как тестировать API
- 🐛 Решение проблем
- 📊 Проверка данных в БД

### `query.sql`
**SQL команда для создания таблицы**
- Копируйте и выполните в PostgreSQL

---

## 🛠️ ОСНОВНЫЕ ФАЙЛЫ ПРОЕКТА

### `server.js` - Express API сервер
```javascript
// Содержит все 4 API endpoints:
POST /api/register   - Регистрация
POST /api/login      - Вход
GET /api/user/:id    - Информация о пользователе
POST /api/logout     - Выход
```

### `.env` - Переменные окружения
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expert_polymer
DB_USER=postgres
DB_PASSWORD=ВАШ_ПАРОЛЬ
PORT=3000
```

### `src/components/LoginModal.vue`
- Форма для входа
- Отправляет запросы на `/api/login`
- Сохраняет сессию

### `src/components/RegisterModal.vue`
- Форма для регистрации
- Отправляет запросы на `/api/register`
- Валидация всех полей

### `src/api/auth.js`
- Готовые функции для работы с API
- Используйте эти функции в компонентах

### `src/App.vue`
- Управление состоянием аутентификации
- Защита страниц для авторизованных пользователей

---

## 🚀 КОМАНДЫ

```bash
# Установка зависимостей
npm install

# Запуск API сервера (порт 3000)
npm run api

# Запуск фронтенда (порт 5173)
npm run dev

# Сборка для продакшена
npm run build

# Просмотр собранного проекта
npm run preview
```

---

## 📡 API ENDPOINTS

| Метод | URL | Описание | Файл |
|-------|-----|---------|------|
| POST | `/api/register` | Регистрация | server.js строка ~50 |
| POST | `/api/login` | Вход | server.js строка ~95 |
| GET | `/api/user/:id` | Получить данные | server.js строка ~150 |
| POST | `/api/logout` | Выход | server.js строка ~175 |

**Примеры запросов:** см. `AUTH_SETUP.md`

---

## 🔐 КЛЮЧЕВЫЕ ФУНКЦИИ

### Регистрация
- ✅ Валидация email
- ✅ Проверка уникальности
- ✅ Хеширование пароля
- ✅ Сохранение в PostgreSQL

### Вход
- ✅ Проверка credentials
- ✅ Генерация токена
- ✅ Опция "Запомнить меня"
- ✅ Сохранение сессии

### Защита
- ✅ Защита страницы Analysis
- ✅ Проверка аутентификации
- ✅ Выход с очисткой данных

---

## 🐛 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Быстрая диагностика

```sql
-- 1. БД запущена?
SELECT version();

-- 2. Таблица существует?
SELECT * FROM users;

-- 3. Данные там?
SELECT COUNT(*) FROM users;
```

```bash
# 4. Сервер работает?
curl http://localhost:3000/api/login

# 5. Фронт работает?
# Откройте http://localhost:5173
```

### Основные проблемы и решения

| Проблема | Решение |
|----------|---------|
| "Database connection error" | Проверьте `.env` и запустите PostgreSQL |
| "Table users not found" | Выполните SQL из `query.sql` |
| "Cannot POST /api/register" | Убедитесь что сервер запущен |
| "CORS error" | Проверьте что сервер на порту 3000 |
| "Duplicate key error" | Пользователь с таким email уже существует |

**Подробно:** см. `TESTING.md`

---

## 📊 СТРУКТУРА ПРОЕКТА

```
expert-polymer/
├── 📄 server.js              ← API сервер (обновлен)
├── 📄 .env                   ← Параметры БД (заполнить!)
├── 📄 query.sql              ← SQL для таблицы
├── 📖 QUICKSTART.md          ← НАЧНИТЕ ОТСЮДА
├── 📖 AUTH_SETUP.md          ← Техническая документация
├── 📖 IMPLEMENTATION_SUMMARY.md ← Резюме всех изменений
├── 📖 TESTING.md             ← Тестирование и диагностика
├── 📄 package.json           ← Зависимости
├── 📄 vite.config.js         ← Конфиг Vite
│
├── src/
│   ├── App.vue               ← Главный компонент (поддерживает auth)
│   ├── main.js
│   │
│   ├── api/
│   │   └── auth.js           ← API функции (обновлено)
│   │
│   └── components/
│       ├── LoginModal.vue         ← Форма входа (обновлена)
│       ├── RegisterModal.vue      ← Форма регистрации (обновлена)
│       ├── NavBar.vue
│       ├── MainPage.vue
│       ├── AnalysisPage.vue
│       ├── ContactsPage.vue
│       ├── AboutPage.vue
│       └── Footer.vue
│
└── public/
    └── (статические файлы)
```

---

## 🎓 ТЕХНОЛОГИИ

- **Frontend**: Vue 3, Vite
- **Backend**: Express.js, Node.js
- **Database**: PostgreSQL
- **API**: REST с JSON
- **Authentication**: Token-based

---

## 🚀 РЕКОМЕНДУЕМЫЙ ПОРЯДОК ЧТЕНИЯ

1. **QUICKSTART.md** (5 мин) - быстрый старт
2. **Запустить проект и протестировать** (10 мин)
3. **AUTH_SETUP.md** (10 мин) - понять API
4. **TESTING.md** (если есть проблемы) - диагностика
5. **IMPLEMENTATION_SUMMARY.md** (для полного понимания)

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- [Express.js документация](https://expressjs.com/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
- [Vue 3 документация](https://vuejs.org/)
- [Vite документация](https://vite.dev/)
- [Node.js pg модуль](https://node-postgres.com/)

---

## 💡 ЧАСТЫЕ ВОПРОСЫ

**Q: Где мой пароль хранится?**
A: В БД в виде хеша SHA256 (в продакшене используйте bcrypt)

**Q: Можно ли использовать в продакшене?**
A: Нет, замените SHA256 на bcrypt и используйте JWT вместо простых токенов

**Q: Как добавить новые поля в регистрацию?**
A: 1) Добавьте колонку в БД, 2) Добавьте поле в форму, 3) Обновите API

**Q: Как защитить другие страницы?**
A: В App.vue добавьте проверку `if (page === 'mypage' && !isAuthenticated.value)`

---

**Вы готовы! Начните с `QUICKSTART.md`** 🎉
