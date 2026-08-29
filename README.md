# Интеллектуальная система анализа полимерных порошков

Объединённый проект: веб-система с ролевым доступом и очередями задач + ядро
экспертной системы, которое по СЭМ-изображению определяет пригодность
полимерного порошка для аддитивного производства.

Пользователь загружает снимок → частицы сегментируются нейросетью YOLOv8-seg →
по контурам считаются морфологические характеристики → нечёткая экспертная
подсистема (Mamdani) выносит заключение о пригодности материала.

---

## Из чего собран проект

Проект получен слиянием трёх независимых кодовых баз:

| Было | Стало | Что это |
|---|---|---|
| `Expert_system_diploma/` | `expert_system/`, `cli.py`, `data/`, `tests/` | Ядро: YOLOv8-seg, морфометрия, нечёткий вывод, SQLite-хранилище, CLI |
| `scientific-system-backend` | `backend/` | FastAPI: JWT, RBAC, инвайты, Celery + Redis, WebSocket, PostgreSQL |
| `expert-polymer` | `frontend/` | Vue 3 + Vite: загрузка снимка, история, админ-часть |

Ключевое изменение при слиянии: раньше backend возвращал **заглушку** —
`ml_service.py` рисовал на изображении один прямоугольник «Mock particle».
Теперь тот же модуль вызывает настоящее ядро и отдаёт в API состав порошка,
морфологию и вердикт экспертной системы.

---

## Структура

```
.
├── expert_system/          # ядро экспертной системы (Python-пакет)
│   ├── config.py           #   классы частиц, пути, пороги (+ override через env)
│   ├── detector.py         #   сегментация YOLOv8-seg
│   ├── metrics.py          #   округлость, эквивалентный диаметр, дисперсность
│   ├── fuzzy_expert.py     #   нечёткий вывод Mamdani (scikit-fuzzy)
│   ├── analyzer.py         #   фасад: полный конвейер анализа
│   ├── storage.py          #   SQLite-хранилище для CLI-режима
│   └── visualization.py    #   отрисовка боксов и масок
│
├── backend/                # веб-часть (FastAPI)
│   ├── app/
│   │   ├── routes/ controllers/ services/ models/ schemas/
│   │   ├── services/ml_service.py   # ← стык веб-части и ядра
│   │   ├── tasks/          #   Celery: асинхронный анализ
│   │   └── static/         #   uploads/ и processed/
│   ├── alembic/            #   миграции БД
│   └── tests/              #   тесты API
│
├── frontend/               # Vue 3 + Vite
│   └── src/api/            #   клиент к /api/* и WebSocket
│
├── data/
│   ├── models/yolo_particles_seg.pt   # веса модели
│   ├── images/             #   примеры СЭМ-снимков
│   └── results/            #   выгрузки CLI
│
├── tests/                  # тесты ядра (метрики, нечёткий вывод)
├── examples/               # автономный пример интеграции ядра
├── docs/postman/           # коллекция Postman для API
├── cli.py                  # запуск анализа из командной строки
├── requirements.txt        # база (без ultralytics/torch)
├── requirements-ml.txt     # база + ultralytics (полный ML-режим)
├── Dockerfile              # образ backend'а (контекст — корень)
└── docker-compose.yml      # db + redis + backend + worker (+ frontend)
```

---

## Как связаны части

```
        браузер (frontend/, Vue 3)
               │  POST /api/analyze     JWT
               ▼
        backend/app/routes/analysis_routes.py
               │
               ▼
        backend/app/services/ml_service.py     ← стык
               │  ML_BACKEND=auto|expert_system|mock
               ▼
        expert_system.Analyzer.analyze()
               │
      ┌────────┴─────────┐
      ▼                  ▼
  detector.py        metrics.py
  (YOLOv8-seg)       (округлость, диаметр,
      │               дисперсность)
      └────────┬─────────┘
               ▼
        fuzzy_expert.py  →  score 0–100, вердикт
               │
               ▼
        result_data в PostgreSQL + processed-изображение
```

Асинхронный путь (`POST /api/analyze/async`) устроен так же, но вызов ядра
происходит в Celery-воркере, а статус задачи уходит на фронт по WebSocket.

---

## Режимы работы ядра

Переключаются переменной `ML_BACKEND`:

| Значение | Поведение |
|---|---|
| `auto` (по умолчанию) | Ядро, если пакет импортируется и найдены веса; иначе заглушка |
| `expert_system` | Только ядро; если недоступно — ошибка при старте анализа |
| `mock` | Только заглушка. Нужна для CI, тестов API и разработки фронтенда без torch |

Дополнительно `ML_STRICT=1` запрещает молчаливый откат на заглушку при ошибке
ядра — задача завершится с ошибкой, а не подсунет фиктивный результат.

---

## Установка

### 1. Зависимости

```bash
python -m venv .venv
.venv\Scripts\activate
```

Полный режим с сегментацией (тянет torch, ~2 ГБ):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-ml.txt
pip install -e .
```

Лёгкий режим — API и фронтенд без нейросети (`ML_BACKEND` сам откатится на `mock`):

```bash
pip install -r requirements.txt
pip install -e .
```

`pip install -e .` делает пакет `expert_system` импортируемым из `backend/`.
Без него backend всё равно найдёт ядро — `ml_service.py` добавляет корень
проекта в `sys.path`, — но установка чище.

### 2. Веса модели

Файл `data/models/yolo_particles_seg.pt` уже лежит в репозитории. При замене
модели путь можно переопределить переменной `ES_MODEL_PATH`.

### 3. Окружение

```bash
copy .env.example .env      # Windows
cp .env.example .env        # Linux / macOS
```

Заполнить `DATABASE_URL`, `SECRET_KEY`, при необходимости `TEST_DATABASE_URL`.
Значение `SECRET_KEY` можно сгенерировать:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Для фронтенда есть свой `frontend/.env.example`, но в режиме разработки он не
обязателен — Vite проксирует запросы на backend сам.

### 4. Фронтенд

```bash
cd frontend
npm install
```

---

## Запуск

### Через Docker (рекомендуется)

```bash
docker compose up --build
```

После применения миграций первого администратора можно создать интерактивной
командой (пароль не попадёт в историю shell):

```bash
docker compose exec backend python -m app.commands.create_admin \
  --email admin@example.com --first-name System --last-name Administrator
```

Команда откажется работать, если администратор уже существует. Дальнейшие роли
назначаются в пункте «Пользователи» меню администратора.

Поднимутся PostgreSQL (порт 5434), Redis, backend (8000) и Celery-воркер.
Миграции применяются автоматически. Фронтенд вынесен в отдельный профиль:

```bash
docker compose --profile frontend up
```

### Быстрый запуск без Postgres, Redis и Docker

Если ничего из этого не установлено, система поднимается на SQLite. Работает
всё, кроме асинхронного анализа через Celery (`/api/analyze/async` и WebSocket) —
для него нужен Redis. Обычный синхронный `/api/analyze` доступен.

Создать базу (один раз):

```bash
cd backend
$env:DATABASE_URL="sqlite:///./dev.db"
python -m app.database.create_tables
```

Alembic здесь не нужен: таблицы создаются напрямую из моделей.

Запустить backend:

```bash
cd backend
$env:DATABASE_URL="sqlite:///./dev.db"
python -m uvicorn app.main:app --port 8000
```

Во втором терминале — фронтенд:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Открыть http://127.0.0.1:5173.

Про `--host 127.0.0.1`: без него Vite на Windows иногда слушает только IPv6
(`::1`), и браузер, резолвящий `localhost` в `127.0.0.1`, не достучится.

Чтобы не выставлять `DATABASE_URL` каждый раз, раскомментируйте строку
`DATABASE_URL=sqlite:///./dev.db` в `.env`.

### Локально с Postgres

Backend (рабочая директория — `backend/`, оттуда резолвятся `app/static` и `alembic.ini`):

```bash
cd backend && alembic upgrade head && uvicorn app.main:app --reload
```

Celery-воркер (на Windows нужен `--pool=solo`):

```bash
cd backend && celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

Фронтенд (Vite проксирует `/api` и `/static` на `localhost:8000`):

```bash
cd frontend && npm run dev
```

- API и Swagger: http://localhost:8000/docs
- Интерфейс: http://localhost:5173

### Ядро из командной строки, без веб-части

```bash
python cli.py data/images/img_00007.png --boxes --masks
python cli.py data/images/ --json data/results/report.json
```

---

## Тесты

Два независимых набора.

Ядро экспертной системы — БД и веса не нужны:

```bash
pytest
```

API — нужен поднятый PostgreSQL и `TEST_DATABASE_URL` в `.env`:

```bash
cd backend && pytest
```

Тесты API прогоняются с `ML_BACKEND=mock` (выставляется в `backend/tests/conftest.py`):
они проверяют контракт HTTP-слоя, а не качество модели, и не должны тянуть в CI
гигабайты весов. Стык веб-части с ядром покрыт отдельно в
`backend/tests/test_ml_service.py` — там проверяется преобразование результата
`Analyzer.analyze()` в структуру ответа API; веса для этого тоже не требуются.

CI (`.github/workflows/tests.yml`) гоняет оба набора отдельными job'ами.

---

## Формат ответа анализа

`result_data` в ответе `/api/analyze` и `/api/results/{id}`:

```jsonc
{
  "image": { "width": 224, "height": 224 },
  "particles_detected": 13,
  "detections": [
    {
      "label": "spherical",
      "confidence": 0.984,
      "bbox": { "x1": 68, "y1": 168, "x2": 98, "y2": 197 },
      "circularity": 0.802,
      "diameter_px": 27.7,
      "area_px": 600.5
    }
  ],
  "composition": { "spherical": 23.1, "fragmented": 46.2, "spongy": 23.1,
                   "dendritic": 7.7, "teardrop": 0.0 },
  "avg_circularity": 0.589,
  "dispersity": 0.507,
  "size_stats": { "min_px": 13.5, "max_px": 66.2, "mean_px": 33.1, "std_px": 16.8 },
  "expert": {
    "score": 15.28,
    "verdict": "unsuitable",
    "conclusion": "Материал не пригоден для аддитивного производства",
    "inputs": { "sphericity": 0.231, "smoothness": 0.589, "uniformity": 0.493 }
  },
  "model": { "name": "yolo_particles_seg", "version": "1.0.0",
             "type": "yolov8-seg+fuzzy" },
  "processing_time_ms": 12814.7
}
```

Блоки `composition`, `avg_circularity`, `dispersity`, `size_stats` и `expert`
необязательные: в режиме `mock` их нет, и записи, сделанные до объединения
проектов, продолжают читаться без миграции.

Классы частиц: `dendritic`, `fragmented`, `spongy`, `spherical`, `teardrop`.
Вердикты: `suitable` (score ≥ 70), `conditional` (≥ 40), `unsuitable`.

---

## Роли и доступ

| Роль | Права |
|---|---|
| `admin` | Полный доступ, управление пользователями, audit logs |
| `director` | Управление своими researcher'ами, invite-коды, история группы |
| `researcher` | Загрузка изображений, только свои исследования |

Подробности по API — в [backend/README.md](backend/README.md) и коллекции
Postman в `docs/postman/`.

---

## Дополнительно

- [docs/expert_system.md](docs/expert_system.md) — методика анализа: метрики,
  база нечётких правил, формат результата ядра, использование как библиотеки
- [backend/README.md](backend/README.md) — эндпоинты, роли, миграции, CI
- `frontend/docs/legacy/` — документация к первой версии фронтенда, когда он
  ходил в собственный Express-сервер (больше не используется)
