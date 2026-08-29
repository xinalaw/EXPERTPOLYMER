# Expert Polymer - Полная инструкция по подключению БД

## 📋 Требования
- Node.js 20.19.0 или выше
- PostgreSQL установлен и запущен
- VS Code с расширением PostgreSQL

## 🔧 Настройка окружения

### 1. Обновите `.env` файл с параметрами вашей БД

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expert_polymer
DB_USER=postgres
DB_PASSWORD=ваш_пароль_postgresql
PORT=3000
```

### 2. Создание таблицы в PostgreSQL

Выполните SQL команду из `query.sql` в вашей базе данных:

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

## 🚀 Запуск проекта

### В одном терминале запустите сервер:
```bash
npm run api
```
Сервер запустится на `http://localhost:3000`

### В другом терминале запустите frontend:
```bash
npm run dev
```
Приложение откроется на `http://localhost:5173`

## 📡 API Endpoints

### Регистрация
**POST** `/api/register`

```json
{
  "firstName": "Иван",
  "lastName": "Иванов",
  "email": "ivan@example.com",
  "password": "password123",
  "organization": "Компания"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Регистрация успешна",
  "user": {
    "id": 1,
    "email": "ivan@example.com",
    "first_name": "Иван",
    "last_name": "Иванов"
  }
}
```

### Вход
**POST** `/api/login`

```json
{
  "email": "ivan@example.com",
  "password": "password123",
  "rememberMe": true
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Вход успешен",
  "token": "hash_token",
  "user": {
    "id": 1,
    "email": "ivan@example.com",
    "firstName": "Иван",
    "lastName": "Иванов",
    "role": "user"
  }
}
```

### Получить информацию о пользователе
**GET** `/api/user/:id`

**Ответ:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "ivan@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "role": "user",
    "created_at": "2025-12-08T..."
  }
}
```

### Выход
**POST** `/api/logout`

**Ответ:**
```json
{
  "success": true,
  "message": "Выход выполнен"
}
```

## 🔐 Особенности

✅ **Регистрация:**
- Валидация email
- Проверка паролей (минимум 6 символов)
- Проверка уникальности email
- Хеширование пароля SHA256
- Сохранение организации (опционально)

✅ **Вход:**
- Проверка email и пароля
- Опция "Запомнить меня"
- Генерация токена
- Сохранение сессии в localStorage/sessionStorage

✅ **Валидация на клиенте:**
- Email формат
- Пароль длина
- Совпадение паролей
- Требуемые поля

## ⚠️ Важные замечания

1. **Пароль:** Используется SHA256 хеширование. В продакшене используйте `bcrypt`!
2. **Токен:** Простой случайный токен. В продакшене используйте JWT!
3. **Подключение:** Убедитесь, что PostgreSQL запущен
4. **CORS:** Сервер принимает запросы с любых источников (для разработки)

## 📱 Структура компонентов

- `LoginModal.vue` - модаль входа
- `RegisterModal.vue` - модаль регистрации  
- `server.js` - Express сервер с API
- `.env` - параметры окружения

## 🐛 Troubleshooting

**Ошибка подключения к БД:**
- Проверьте, что PostgreSQL запущен
- Убедитесь в правильности параметров в `.env`
- Проверьте пароль к PostgreSQL

**Ошибка CORS:**
- Убедитесь, что сервер запущен на порту 3000
- Проверьте, что фронт обращается к `http://localhost:3000`

**Таблица не найдена:**
- Выполните SQL из `query.sql`
- Проверьте имя базы данных в `.env`
