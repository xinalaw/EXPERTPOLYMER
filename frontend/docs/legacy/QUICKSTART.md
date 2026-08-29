# 🚀 БЫСТРЫЙ СТАРТ - Аутентификация с PostgreSQL

## ШАГ 1️⃣: Обновите `.env` файл

Откройте файл `.env` и установите правильные параметры вашей PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expert_polymer
DB_USER=postgres
DB_PASSWORD=ВАШ_ПАРОЛЬ_СЮДА
PORT=3000
```

**Где найти параметры:**
- `DB_HOST` - хост БД (обычно localhost)
- `DB_PORT` - порт (обычно 5432)
- `DB_NAME` - имя базы данных которую вы создали
- `DB_USER` - пользователь (обычно postgres)
- `DB_PASSWORD` - пароль который вы установили при установке PostgreSQL

---

## ШАГ 2️⃣: Создайте таблицу в PostgreSQL

Используя VS Code расширение PostgreSQL:

1. Откройте расширение PostgreSQL в левой панели
2. Найдите вашу базу данных `expert_polymer`
3. Нажмите правой кнопкой → "New Query"
4. Скопируйте и выполните этот SQL:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    organization VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

---

## ШАГ 3️⃣: Запустите сервер

В терминале VS Code выполните:

```bash
npm run api
```

Вы должны увидеть:
```
Server running on http://localhost:3000
Database connected: ...
```

---

## ШАГ 4️⃣: Запустите фронт

Откройте ЕЩЕ ОДИН терминал и выполните:

```bash
npm run dev
```

Вы должны увидеть:
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

---

## ✅ ГОТОВО!

Теперь вы можете:
1. Открыть браузер: `http://localhost:5173/`
2. Нажать "Вход" или "Регистрация"
3. Заполнить форму
4. Данные будут сохранены в PostgreSQL! 🎉

---

## 🔍 Проверка работы

### Проверить что сервер работает:
```bash
curl http://localhost:3000/api/login
```

### Проверить таблицу в PostgreSQL:
```sql
SELECT * FROM users;
```

---

## ❌ Если что-то не работает

### Ошибка: "Database connection error"
- Проверьте что PostgreSQL запущен
- Проверьте параметры в `.env`
- Проверьте пароль к PostgreSQL

### Ошибка: "cannot find module 'pg'"
- Выполните: `npm install`

### Ошибка: "CORS error"
- Убедитесь что сервер запущен на порту 3000
- Убедитесь что фронт обращается к `http://localhost:3000`

---

## 📝 Структура

```
expert-polymer/
├── server.js          ← Express API сервер
├── .env              ← Параметры БД (заполните!)
├── package.json      ← Зависимости
├── query.sql         ← SQL для создания таблицы
└── src/
    └── components/
        ├── LoginModal.vue      ← Форма входа
        └── RegisterModal.vue   ← Форма регистрации
```

---

**Нужна помощь?** Проверьте `AUTH_SETUP.md` для подробной документации API
