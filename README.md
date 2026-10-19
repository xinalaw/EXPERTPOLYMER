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
| `scientific-system-backend` | `backend/` | FastAPI: JWT, RBAC, инвайты, Celery + Redis, PostgreSQL |
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
│   └── src/api/            #   клиент к backend API
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
├── docker-compose.yml      # db + redis + backend + worker + frontend
├── docker-compose.mock.yml # быстрый вариант без torch
└── scripts/docker-up.sh    # короткая команда запуска
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
происходит в Celery-воркере, а frontend получает статус через защищённый
`GET /api/analyze/tasks/{task_id}`.

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

Для Docker локальная установка Python и Node.js не требуется; переходите к
[запуску через Docker](#через-docker-рекомендуется).

### 1. Зависимости

```bash
python -m venv .venv
.venv\Scripts\activate
```

Полный режим с сегментацией (тянет torch, ~2 ГБ):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-ml.txt
pip install --no-deps -e .
```

Лёгкий режим — API и фронтенд без нейросети (`ML_BACKEND` сам откатится на `mock`):

```bash
pip install -r requirements.txt
pip install --no-deps -e .
```

`pip install --no-deps -e .` делает пакет `expert_system` импортируемым из `backend/`.
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
npm ci
```

---

## Запуск

### Через Docker (рекомендуется)

Нужен Docker с Compose v2. Все команды ниже выполняются из корня проекта.
В Docker Desktop для WSL включите **Settings → Resources → WSL Integration**
для своего дистрибутива, затем проверьте `docker compose version`.
Локальные Python, Node.js, PostgreSQL и Redis устанавливать не нужно.

**Самый быстрый первый запуск, без загрузки torch:**

```bash
./scripts/docker-up.sh --mock
```

Скрипт запускает весь стек: новый frontend, API с админ-панелью, PostgreSQL,
Redis и Celery. Он ждёт готовности сервисов; миграции применяются автоматически
до запуска API и воркера. Файлы `.env` скрипт не создаёт и не меняет: для
локального запуска достаточно встроенных значений. Свои настройки можно
задать по [.env.example](.env.example); для постоянного окружения замените
`SECRET_KEY` и пароль БД перед первым запуском.

Без shell-скрипта (в том числе в PowerShell) та же команда:

```bash
docker compose -f docker-compose.yml -f docker-compose.mock.yml up -d --build --wait
```

| Что открыть | Адрес |
|---|---|
| Интерфейс | http://localhost:5173 |
| Админ-панель после входа администратором | http://localhost:5173/#/admin |
| API / Swagger | http://localhost:8000/docs |
| PostgreSQL с хоста | `localhost:5434` |
| Redis с хоста | `localhost:6379` |

В режиме `mock` нейросеть не запускается: анализ возвращает демонстрационную
разметку без экспертной оценки. Этот режим подходит для проверки интерфейса,
регистрации, ролей, истории и админ-панели.

**Первый администратор** создаётся один раз после запуска:

```bash
docker compose exec backend python -m app.commands.create_admin \
  --email admin@example.com --first-name System --last-name Administrator
```

В PowerShell выполните команду одной строкой. Пароль вводится интерактивно
дважды и не попадает в историю shell. Команда откажется создавать ещё одного
администратора, если он уже существует. Войдите с этим email в интерфейсе;
дальнейшие роли назначаются в разделе «Пользователи» админ-панели.

**Повторный запуск:**

```bash
./scripts/docker-up.sh --mock
```

Зависимости Python и `npm ci` кэшируются в образах; без изменения файлов
зависимостей они повторно не скачиваются. Frontend включён в образ, поэтому
эта же команда пересобирает его после изменений исходников. Для разработки
с горячим обновлением запускайте Vite локально, как описано ниже.

**Полный ML-режим** с CPU torch и настоящей сегментацией остаётся стандартным
поведением основного Compose:

```bash
docker compose up -d --build --wait
```

Первый запуск дольше из-за загрузки CPU torch/torchvision и ultralytics.
Используется `ML_BACKEND=auto`: при доступном ядре и весах работает нейросеть.
Веса `data/models/yolo_particles_seg.pt` подключены с хоста; после их замены
достаточно `docker compose restart backend worker`. Если ранее вы прописали
`ML_BACKEND=mock` в `.env`,
для настоящего анализа измените его на `auto` или `expert_system`.
Для строгого режима задайте `ML_BACKEND=expert_system` и `ML_STRICT=1` в `.env`.
Переход между mock и ML использует ту же БД и загруженные файлы.

**Состояние, логи и остановка** для обоих режимов:

```bash
docker compose ps
docker compose logs -f backend worker frontend
docker compose down
```

`down` сохраняет именованные тома `postgres_data` (пользователи, роли, история)
и `redis_data` (очередь), а также изображения в `backend/app/static/uploads`
и `backend/app/static/processed`. Не добавляйте `-v`, если нужны данные.
Пароль и имя существующей PostgreSQL БД сохраняются внутри тома: изменение
`DB_*` в `.env` само по себе их не меняет.

### Быстрый запуск без Postgres, Redis и Docker

Если ничего из этого не установлено, система поднимается на SQLite. Работает
всё, кроме асинхронного анализа через Celery (`/api/analyze/async`) —
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
- [frontend/README.md](frontend/README.md) — клиентское приложение и единая
  админ-панель
