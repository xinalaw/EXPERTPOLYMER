# 🔧 ДИАГНОСТИКА И ТЕСТИРОВАНИЕ

## ✅ Чек-лист перед запуском

### 1. PostgreSQL
- [ ] PostgreSQL установлен и запущен
- [ ] Расширение PostgreSQL установлено в VS Code
- [ ] Вы видите список баз данных в расширении

### 2. Node.js
- [ ] Node.js версии 20.19.0 или выше
- [ ] npm установлен
```bash
node -v
npm -v
```

### 3. Проект
- [ ] Зависимости установлены (`node_modules` существует)
- [ ] Все файлы на месте:
  - [ ] `server.js` существует
  - [ ] `.env` существует
  - [ ] `query.sql` существует
  - [ ] `package.json` существует

---

## 🔍 Тестирование БД

### Подключение к PostgreSQL

**В VS Code:**
1. Откройте расширение PostgreSQL (иконка слева)
2. Найдите ваш сервер в списке
3. Разверните его → должна быть БД `expert_polymer`
4. Разверните БД → должна быть таблица `users`

**Или через командную строку:**
```bash
psql -U postgres -d expert_polymer
```

### Проверить что таблица создана

В расширении PostgreSQL или в psql:
```sql
SELECT * FROM users;
```

Должен вернуть пустую таблицу (0 строк) если только что создана.

### Проверить структуру таблицы

```sql
\d users
```

Должны быть поля:
- id (SERIAL, PRIMARY KEY)
- email (VARCHAR)
- password_hash (VARCHAR)
- first_name (VARCHAR)
- last_name (VARCHAR)
- organization (VARCHAR)
- role (VARCHAR)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- is_active (BOOLEAN)

---

## 🚀 Запуск и тестирование

### Запуск сервера

```bash
cd c:\Users\Sayfu\Desktop\Kursovaya\expert-polymer
npm run api
```

**Успешно если видите:**
```
Server running on http://localhost:3000
Database connected: ...
```

**Ошибки:**
```
Error: connect ECONNREFUSED 127.0.0.1:5432
→ PostgreSQL не запущен или неправильные параметры в .env
```

```
Error: permission denied for schema public
→ Проблемы с пермиссиями в БД
```

### Запуск фронтенда

В НОВОМ терминале:
```bash
npm run dev
```

**Успешно если видите:**
```
VITE v7.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

---

## 🧪 Тестирование API

### Способ 1: Через cURL (командная строка)

**Регистрация:**
```bash
curl -X POST http://localhost:3000/api/register ^
  -H "Content-Type: application/json" ^
  -d "{\"firstName\":\"Иван\",\"lastName\":\"Иванов\",\"email\":\"ivan@test.com\",\"password\":\"password123\",\"organization\":\"Test Corp\"}"
```

**Вход:**
```bash
curl -X POST http://localhost:3000/api/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"ivan@test.com\",\"password\":\"password123\",\"rememberMe\":true}"
```

### Способ 2: Через Postman или REST Client

**POST http://localhost:3000/api/register**
```json
{
  "firstName": "Иван",
  "lastName": "Иванов",
  "email": "ivan@test.com",
  "password": "password123",
  "organization": "Test Corp"
}
```

**POST http://localhost:3000/api/login**
```json
{
  "email": "ivan@test.com",
  "password": "password123",
  "rememberMe": true
}
```

### Способ 3: Через браузер

1. Откройте http://localhost:5173/
2. Нажмите кнопку "Регистрация"
3. Заполните форму
4. Нажмите "Зарегистрироваться"
5. Должна появиться новая строка в БД

---

## 📊 Проверка данных в БД

### Просмотр всех пользователей

```sql
SELECT id, email, first_name, last_name, created_at FROM users;
```

### Проверить конкретного пользователя

```sql
SELECT * FROM users WHERE email = 'ivan@test.com';
```

### Удалить тестового пользователя

```sql
DELETE FROM users WHERE email = 'ivan@test.com';
```

### Очистить всю таблицу

```sql
TRUNCATE TABLE users;
```

---

## 🐛 Поиск и решение проблем

### Проблема: "Cannot POST /api/register"

**Диагностика:**
```bash
# 1. Проверить что сервер запущен
curl http://localhost:3000

# 2. Проверить что сервер работает
curl http://localhost:3000/api/login
```

**Решение:**
- Убедитесь что выполнили `npm run api` в терминале
- Проверьте что нет ошибок в консоли сервера

### Проблема: "Error connecting to database"

**Диагностика:**
```sql
-- В PostgreSQL проверить что БД существует
SELECT datname FROM pg_database WHERE datname = 'expert_polymer';

-- Проверить что таблица существует
SELECT * FROM information_schema.tables WHERE table_name = 'users';
```

**Решение:**
- Проверьте параметры в `.env`
- Убедитесь что PostgreSQL запущен
- Проверьте пароль к PostgreSQL

### Проблема: "Duplicate key value violates unique constraint"

**Диагностика:**
```sql
-- Проверить дублирующиеся emails
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
```

**Решение:**
- Пользователь с таким email уже существует
- Используйте другой email или удалите старого пользователя

### Проблема: "CORS error" в браузере

**Диагностика:**
- Откройте DevTools (F12) → Console
- Проверьте URL в ошибке

**Решение:**
- Убедитесь что фронт обращается к `http://localhost:3000`
- Убедитесь что сервер запущен на порту 3000
- Проверьте что CORS разрешен в `server.js`

### Проблема: Форма не отправляется

**Диагностика:**
- Откройте DevTools → Network
- Попробуйте заполнить форму и отправить
- Смотрите появился ли запрос

**Решение:**
- Проверьте валидацию формы (красные подсказки)
- Убедитесь что все поля заполнены корректно
- Проверьте консоль на ошибки JavaScript

---

## 📈 Мониторинг

### Логирование регистраций

```sql
-- Просмотреть новых пользователей за последний час
SELECT email, first_name, last_name, created_at 
FROM users 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

### Статистика пользователей

```sql
-- Всего пользователей
SELECT COUNT(*) as total_users FROM users;

-- Активных пользователей
SELECT COUNT(*) as active_users FROM users WHERE is_active = TRUE;

-- Пользователей по ролям
SELECT role, COUNT(*) FROM users GROUP BY role;
```

### Проверка целостности данных

```sql
-- Проверить что нет NULL в важных полях
SELECT * FROM users WHERE email IS NULL OR password_hash IS NULL;

-- Проверить что email уникален
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
```

---

## 📝 Логи сервера

### Включить подробное логирование

В `server.js` добавьте перед `app.listen()`:

```javascript
// Логирование всех запросов
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`)
  console.log('Body:', req.body)
  next()
})

// Логирование ошибок
app.use((err, req, res, next) => {
  console.error('Error:', err)
  res.status(500).json({ error: err.message })
})
```

### Просмотр логов в консоли

Когда сервер запущен:
1. Откройте браузер
2. Попробуйте зарегистрироваться
3. В консоли где запущен сервер должны быть логи:

```
2025-12-08T10:00:00.000Z POST /api/register
Body: { firstName: 'Иван', ... }
```

---

## ✅ Финальная проверка

Все работает если:
- [ ] Сервер запущен без ошибок
- [ ] Фронт запущен и видно на http://localhost:5173
- [ ] Форма регистрации отправляется
- [ ] Нет ошибок в консоли браузера
- [ ] Нет ошибок в консоли сервера
- [ ] Данные появляются в PostgreSQL таблице
- [ ] Можно залогиниться с созданным пользователем

---

**Если все пункты выполнены - система полностью рабочая! 🎉**
