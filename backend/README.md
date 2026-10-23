# Scientific System Backend

Backend часть интеллектуальной системы анализа полимерных композиционных материалов.

> Это одна из трёх частей объединённого проекта. Общее описание, установка и
> запуск всего стека — в [корневом README](../README.md).
> Ядро анализа лежит рядом, в пакете `expert_system/`; стык с ним —
> `app/services/ml_service.py`.

---

# Технологии

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- OpenCV
- JWT Authentication
- Docker
- Docker Compose
- pytest
- Github Actions CI
- Redis
- Celery

---

# Возможности системы

## Authentication & Authorization

- регистрация пользователей
- JWT авторизация
- RBAC (Role-Based Access Control)

---

## Roles

### admin

- полный доступ к системе
- управление пользователями
- просмотр audit logs
- назначение director/researcher

### director

- управление researcher своей группы
- создание invite-code
- просмотр истории исследований своей группы

### researcher

- загрузка изображений
- просмотр только своих исследований

---

## Invite System

- многоразовые invite-code
- ограничение времени действия invite
- привязка researcher к director

---

## Async Analysis System

- загрузка изображений
- сегментация частиц YOLOv8-seg (пакет `expert_system`)
- расчёт морфологии: округлость, эквивалентный диаметр, дисперсность
- нечёткий вывод Mamdani: оценка пригодности порошка и вердикт
- генерация processed image с разметкой частиц
- JSON result_data
- history API
- асинхронный анализ изображений
- фоновые задачи Celery 
- Redis
- отслеживание статуса задач
- защищённый polling статуса задачи

---

## Administration

- dashboard со сводной статистикой
- единая Vue-панель для пользователей, анализов, задач, инвайтов и журнала
- audit logs
- pagination
- filtering
- user search

---

# Архитектура проекта

```text
backend/            # ← вы здесь; .github/, requirements.txt и Dockerfile — в корне
│
├── alembic/
│
├── app/
│   ├── controllers/
│   ├── middleware/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── database/
│   └── static/
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_invites.py
│   └── test_analysis.py
│
├── pytest.ini
└── README.md
```

`Dockerfile`, `docker-compose.yml`, `requirements*.txt` и `docs/` находятся в корне репозитория.

---

# Docker запуск (Рекомендуется)

## Запуск

Из корня репозитория (миграции выполняются автоматически):

```bash
./scripts/docker-up.sh --mock
```

Быстрый режим использует заглушку анализа без загрузки PyTorch и весов YOLO.
Для полного ML-стека и остальных команд см. [корневой README](../README.md).

Первого администратора создайте один раз; команда интерактивно запросит пароль:

```bash
docker compose exec backend python -m app.commands.create_admin --email admin@example.com
```

Войдите с этой учётной записью в интерфейсе `http://localhost:5173` и откройте
`/admin`. Последующим пользователям роли назначаются в панели администратора.

---

## Swagger

```text
http://127.0.0.1:8000/docs
```

---

## Остановка

```bash
docker compose down
```

---

# Local Development

## 1. Клонирование проекта

```bash
git clone <repository_url>
cd <папка проекта>
```

Виртуальное окружение и зависимости — общие для всего проекта, поэтому
создаются в корне, а не в `backend/`.

---

## 2. Создание виртуального окружения

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

---

## 3. Установка зависимостей

Из корня проекта:

```bash
pip install -r requirements-ml.txt   # с сегментацией YOLOv8 (тянет torch)
pip install -e .                     # пакет expert_system
```

Без нейросети (API будет отвечать заглушкой) достаточно
`pip install -r requirements.txt`.

---

## 4. Создание .env

Создать файл:

```text
.env
```

на основе:

```text
.env.example
```

---

## 5. PostgreSQL

Создать БД:

```text
scientific_system
```

---

## 6. Alembic migrations

```bash
cd backend
alembic upgrade head
```

---

## 7. Запуск backend

```bash
uvicorn app.main:app --reload
```

---

# Swagger

```text
http://127.0.0.1:8000/docs
```

---

# Основные endpoint’ы

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

---

## Analysis

```text
POST   /api/analyze
POST   /api/analyze/async
GET    /api/analyze/tasks/{task_id}
GET    /api/history
GET    /api/results/{id}
DELETE /api/results/{id}
```

---

## Invites

```text
POST /api/invites
GET  /api/invites/{code}
POST /api/invites/{code}/accept
```

---

## Users

```text
GET /api/users
GET /api/users/search
PATCH /api/users/{id}/role
PATCH /api/users/{id}/director
DELETE /api/users/{id}
```

---

## Admin panel

```text
GET /api/admin/dashboard
GET /api/admin/tasks
GET /api/admin/invites
GET /api/director/researchers
```

`/api/admin/*`, управление пользователями и журнал доступны только `admin`.
История анализов фильтруется по правам текущего пользователя; `date=YYYY-MM-DD`
задаёт календарный день UTC, `limit` и `offset` управляют страницами.

---

## Logs

```text
GET /api/logs
```

---

# Примеры API ответов

## POST /api/analyze

Пример ответа:

```json
{
  "id": 1,
  "image_path": "/static/uploads/image.jpg",
  "processed_image_path": "/static/processed/processed_image.jpg",
  "original_filename": "sample.jpg",
  "result": "Изображение обработано. Найдены частицы",
  "confidence": 0.95,
  "width": 1920,
  "height": 1080,
  "result_data": {
    "image": {
      "width": 1920,
      "height": 1080
    },
    "detections": [
      {
        "label": "spherical",
        "confidence": 0.984,
        "bbox": {
          "x1": 68,
          "y1": 168,
          "x2": 98,
          "y2": 197
        },
        "circularity": 0.802,
        "diameter_px": 27.7,
        "area_px": 600.5
      }
    ],
    "particles_detected": 13,
    "expert": {
      "score": 15.28,
      "verdict": "unsuitable",
      "conclusion": "Материал не пригоден для аддитивного производства"
    },
    "model": {
      "name": "yolo_particles_seg",
      "version": "1.0.0",
      "type": "yolov8-seg+fuzzy"
    },
    "processing_time_ms": 12814.7
  },
  "created_at": "2026-05-17T15:00:00"
}
```

---

## JWT Authentication

Для защищённых endpoint необходимо передавать access token:

```text
Authorization: Bearer <token>
```

---

## Роли пользователей

Система поддерживает следующие роли:

```text
admin
director
researcher
```

---

## Analysis Pipeline

Текущий pipeline обработки изображения:

```text
upload image
↓
сегментация частиц (YOLOv8-seg)
↓
морфологические метрики по контурам
↓
нечёткий вывод Mamdani → score и вердикт
↓
processed image saving
↓
result_data generation
```

# Async Analysis Pipeline

Асинхронная обработка изображений реализована через Celery и Redis.

Pipeline:

```text
upload image
↓
FastAPI API
↓
Redis queue
↓
Celery worker
↓
ML processing
↓
PostgreSQL result saving
↓
task status update
```

Поддерживаемые статусы задач:

```text
PENDING
PROCESSING
RETRY
SUCCESS
FAILURE
```
# Testing 

## Postman Collection

Postman API сценарии:
```text
../docs/postman/Scientific System API.postman_collection.json
```

## Pytest

Из `backend/` с отдельной тестовой базой (тесты пересоздают её таблицы):

```bash
export TEST_DATABASE_URL=postgresql+psycopg2://postgres:admin@localhost:5434/scientific_system_test
pytest
```

Для проверки API без PostgreSQL можно использовать
`TEST_DATABASE_URL=sqlite:////tmp/expertpolymer-test.db pytest`.

## Coverage

Запуск тестов с coverage:

```text
pytest --cov=app --cov-report=term-missing
```

# Githunb Action CI
В проекте используется GitHub Actions для автоматического тестирования бэкэнда при каждом изменении (push).

CI pipeline:
- запускает PostgreSQL
- устанавливает зависимости
- запускает интеграционные тесты pytest

# Frontend Integration

Frontend должен использовать JWT access token:

```text
Authorization: Bearer <token>
```

Документация API доступна через Swagger.

---

# Автор

Backend Developer — Aizat Vafin
