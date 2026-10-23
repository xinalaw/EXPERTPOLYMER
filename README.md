# Expert Polymer — анализ полимерных порошков

[Описание проекта](#описание-проекта) · [Установка](#установка) · [Быстрый запуск](#быстрый-запуск)

## Описание проекта

Expert Polymer — система анализа СЭМ-изображений полимерных порошков для
оценки их пригодности к аддитивному производству.

Пользователь загружает изображение в браузере. YOLOv8-seg выделяет частицы,
система рассчитывает их морфологические характеристики, а нечёткая экспертная
подсистема Mamdani формирует оценку от 0 до 100 и заключение о пригодности
материала. Результат и изображение с разметкой сохраняются в истории.

### Возможности

- Сегментация частиц и определение их классов: дендритные, осколочные,
  губчатые, сферические и каплевидные.
- Расчёт состава порошка, округлости, размеров частиц и дисперсности.
- Экспертные заключения: материал пригоден, условно пригоден или непригоден.
- Регистрация, авторизация, история исследований и выгрузка JSON-отчётов.
- Синхронный анализ через API и фоновые задачи Celery с отслеживанием статуса.
- Админ-панель: обзор системы, пользователи, история анализов, задачи,
  инвайты и журнал действий.
- Анализ из командной строки без веб-интерфейса.

### Роли

| Роль         | Доступ                                                                                       |
| ------------ | -------------------------------------------------------------------------------------------- |
| `admin`      | Все исследования, управление ролями и назначением директоров, админ-панель и журнал действий |
| `director`   | Исследователи своей группы, их история и invite-коды                                         |
| `researcher` | Загрузка изображений и собственные исследования                                              |

Новые пользователи регистрируются как исследователи. Первого администратора
создаёт отдельная команда; дальнейшие роли назначаются в админ-панели.

### Архитектура

```text
Vue 3 + TypeScript
        │ HTTP / JWT
        ▼
FastAPI ─────── PostgreSQL: пользователи, роли, история, задачи, журнал
        │
        ├── Синхронный анализ
        └── Redis → Celery: фоновый анализ
                        │
                        ▼
               Ядро expert_system
               YOLOv8-seg → метрики → Mamdani
```

Веб-интерфейс отправляет анализ синхронно. Фоновый режим доступен через
`POST /api/analyze/async`, его статус — через `GET /api/analyze/tasks/{task_id}`.
Оба режима используют одно ядро анализа.

```text
expert_system/             # Сегментация, морфометрия, нечёткий вывод, CLI-хранилище
backend/                   # FastAPI, роли, админские API, Celery, миграции
frontend/                  # Vue 3, TypeScript, Vue Router, админ-панель
data/models/               # Веса YOLOv8-seg
data/images/               # Пример СЭМ-изображения
data/results/              # Результаты CLI
tests/                     # Тесты ядра
backend/tests/             # Тесты API
frontend/e2e/              # Браузерные тесты
docs/                      # Методика анализа и документация интеграции
cli.py                     # Точка входа для CLI
requirements.txt           # Python-зависимости без torch и ultralytics
requirements-ml.txt        # Полный набор Python-зависимостей
Dockerfile                 # Образы backend, worker и frontend
docker-compose.yml         # Полный стек
docker-compose.mock.yml    # Вариант без нейросети
scripts/docker-up.sh       # Запуск с автоматической сборкой
```

### Режимы анализа

| `ML_BACKEND`    | Поведение                                                   |
| --------------- | ----------------------------------------------------------- |
| `expert_system` | Настоящий анализ; требует torch, ultralytics и веса модели  |
| `auto`          | Настоящий анализ при доступном ядре и весах; иначе заглушка |
| `mock`          | Демонстрационная разметка без нейросети и экспертной оценки |

Для полного режима инструкции ниже используют `ML_BACKEND=expert_system`
и `ML_STRICT=1`: ошибка модели завершает анализ с ошибкой, без подмены
результата заглушкой. GPU не требуется: предусмотрена CPU-сборка PyTorch.

### Подробная документация

- [Методика экспертной системы](docs/expert_system.md): метрики, нечёткие правила,
  формат результатов и использование ядра как библиотеки.
- [Backend](backend/README.md): API, роли, миграции и тесты.
- [Frontend](frontend/README.md): интерфейс, маршруты, сборка и тесты.
- [Интеграция админ-панели](docs/admin_integration_report.md).
- [Коллекция Postman](docs/postman/).

## Установка

Выполняется один раз и повторяется при обновлении зависимостей или образов.
Все команды этого раздела начинаются **из корня репозитория** — папки,
где находится `docker-compose.yml`.

Выбери способ подготовки:

| Способ                                                        | Что установить на компьютер                                                           |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Весь проект в Docker — основной вариант                       | Docker с Compose v2                                                                   |
| Локальные API, worker и frontend; PostgreSQL и Redis в Docker | Python 3.11+, Node.js из ветки 22 версии 22.12+ либо из ветки 24, Docker с Compose v2 |
| Локальный деморежим на SQLite                                 | Python 3.11+ и тот же Node.js; Docker не нужен                                        |

Для WSL включи свой дистрибутив в **Docker Desktop → Settings → Resources →
WSL Integration**. Для локальной установки в Linux также нужны системные
библиотеки OpenCV; в Ubuntu/Debian это пакеты `libgl1` и `libglib2.0-0`.

### 1. Файл настроек

Создай `.env` из примера, сохранив существующий файл, если он уже есть.

**Linux / macOS / WSL:**

```bash
test -f .env || cp .env.example .env
```

**Windows PowerShell:**

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Для полного функционала установи в `.env`:

```dotenv
ML_BACKEND=expert_system
ML_STRICT=1
```

Задай собственный `SECRET_KEY`. Настройки PostgreSQL и Redis в
[.env.example](.env.example) уже подходят для команд ниже: PostgreSQL доступен
с хоста на порту `5434`, Redis — на `6379`. При изменении пользователя,
пароля или имени БД обнови и `DB_*`, и локальный `DATABASE_URL`.
Внутри Docker адреса БД и Redis задаёт Compose.

Веса `data/models/yolo_particles_seg.pt` включены в репозиторий.
Для локального запуска с другой моделью задай абсолютный `ES_MODEL_PATH`;
для стандартных весов оставь эту переменную незаданной. В Docker путь модели
фиксирован в Compose: для замены весов обнови файл
`data/models/yolo_particles_seg.pt`, сохранив его имя.

### 2. Установка для Docker

Локальные Python, Node.js и venv для этого варианта не нужны.

**Полный функционал, включая нейросеть:**

```bash
docker compose pull db redis
docker compose build
```

Первая сборка загружает CPU-версии torch/torchvision и ultralytics.
Зависимости кэшируются в образах.

**Альтернатива — без torch, для разработки интерфейса и админки:**

```bash
docker compose pull db redis
docker compose -f docker-compose.yml -f docker-compose.mock.yml build
```

Выбери один вариант сборки. При переходе между полным и демонстрационным
режимами повтори соответствующую сборку. Затем переходи к
[быстрому запуску](#быстрый-запуск).

### 3. Установка для локального запуска

Этот подраздел нужен, если Python и frontend будут работать на компьютере.
Для варианта целиком в Docker его можно пропустить.

#### Виртуальное окружение

**Linux / macOS / WSL:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Если PowerShell запрещает активацию скрипта, разреши её для текущего терминала:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

#### Python-зависимости — выбери один набор

**Полный функционал с настоящей сегментацией:**

```bash
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-ml.txt
python -m pip install --no-deps -e .
```

**Альтернатива — без torch и ultralytics:**

```bash
python -m pip install -r requirements.txt
python -m pip install --no-deps -e .
```

`--no-deps` обязателен для лёгкого варианта: зависимости уже установлены
из requirements, а обычный `pip install -e .` дополнительно подтянет нейросеть.

#### Frontend

```bash
cd frontend
npm ci
cd ..
```

Отдельный `.env` для frontend не нужен: Vite проксирует `/api` и `/static`
на backend. При необходимости цель прокси задаётся через `API_PROXY_TARGET`.

Для полного локального варианта подготовь образы инфраструктуры:

```bash
docker compose pull db redis
```

## Быстрый запуск

Команды рассчитаны на выполненную [установку](#установка).
**Каждый новый терминал открывай в корне репозитория**, если не указано иное.
Устанавливать зависимости повторно не нужно.

### 1. Полный запуск через Docker — основной вариант

Поднимает весь функционал: настоящую сегментацию и экспертную оценку,
frontend, API, админ-панель, PostgreSQL, Redis и Celery.

```bash
docker compose up -d --wait
```

Миграции применяются автоматически. Venv активировать не нужно: Python
работает внутри контейнеров. Для повторного запуска используй ту же команду.

После первого запуска создай администратора:

```bash
docker compose exec backend python -m app.commands.create_admin --email admin@example.com
```

Пароль вводится интерактивно дважды. Если администратор уже существует,
повторять команду не нужно. Войди с этим email и открой «Админ-панель»
в основном меню.

| Сервис                   | Адрес                         |
| ------------------------ | ----------------------------- |
| Интерфейс                | http://localhost:5173         |
| Админ-панель после входа | http://localhost:5173/#/admin |
| API / Swagger            | http://localhost:8000/docs    |

### 2. Полный локальный запуск с venv

PostgreSQL и Redis работают в Docker, остальные процессы — локально.
Нужны полный набор Python-зависимостей и настройки полного режима из раздела
«Установка». API запускай перед worker, чтобы сначала применились миграции.

#### Терминал 1 — PostgreSQL и Redis

```bash
docker compose up -d --wait db redis
```

Команда работает в фоне; после её завершения терминал можно использовать
для создания администратора.

#### Терминал 2 — API

**Linux / macOS / WSL:**

```bash
source .venv/bin/activate
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Терминал 3 — Celery worker

**Linux / macOS / WSL:**

```bash
source .venv/bin/activate
cd backend
python -m celery -A app.tasks.celery_app worker --loglevel=info
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

#### Терминал 4 — frontend

Venv для Node.js не нужен. Эти команды одинаковы для Bash и PowerShell:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Интерфейс: http://127.0.0.1:5173. API / Swagger: http://127.0.0.1:8000/docs.

#### Первый администратор — один раз

В свободном терминале из корня проекта:

**Linux / macOS / WSL:**

```bash
source .venv/bin/activate
cd backend
python -m app.commands.create_admin --email admin@example.com
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m app.commands.create_admin --email admin@example.com
```

### 3. Docker без torch

Используй после сборки лёгких образов. Интерфейс, роли, админ-панель,
история и фоновые задачи доступны; анализ возвращает демонстрационную разметку
без нейросети и экспертной оценки.

```bash
docker compose -f docker-compose.yml -f docker-compose.mock.yml up -d --wait
```

Адреса и команда создания администратора те же, что в полном Docker-варианте.
Для повторного запуска используй эту же команду с обоими Compose-файлами.

### 4. Локально без torch, PostgreSQL, Redis и Docker

Используй лёгкий набор Python-зависимостей. База — SQLite,
анализ — демонстрационный. Фоновые задачи Celery в этом варианте недоступны.

#### Терминал 1 — API

**Linux / macOS / WSL:**

```bash
source .venv/bin/activate
export DATABASE_URL=sqlite:///./dev.db
export ML_BACKEND=mock
cd backend
python -m app.database.create_tables
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "sqlite:///./dev.db"
$env:ML_BACKEND = "mock"
cd backend
python -m app.database.create_tables
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Создание таблиц можно повторять: существующие данные сохраняются.
Alembic в этом варианте не используется.

#### Терминал 2 — frontend

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Интерфейс: http://127.0.0.1:5173.

#### Первый администратор для SQLite — один раз

Задай тот же адрес БД в отдельном терминале.

**Linux / macOS / WSL:**

```bash
source .venv/bin/activate
export DATABASE_URL=sqlite:///./dev.db
cd backend
python -m app.commands.create_admin --email admin@example.com
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "sqlite:///./dev.db"
cd backend
python -m app.commands.create_admin --email admin@example.com
```

### 5. Только ядро анализа, без веб-части

Нужна полная локальная установка с torch и весами модели.
PostgreSQL, Redis, API и frontend для CLI не требуются.

**Linux / macOS / WSL:**

```bash
source .venv/bin/activate
python cli.py data/images/img_00007.png --boxes --masks --json data/results/report.json
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
python cli.py data/images/img_00007.png --boxes --masks --json data/results/report.json
```

Изображения с разметкой и JSON сохраняются в `data/results/`, история CLI —
в `expert_system.db`. CLI использует стандартные пути; настройки `ES_*`
для него задаются переменными окружения терминала, `.env` автоматически
не загружается.

### Состояние и остановка

Состояние Docker-сервисов и логи:

```bash
docker compose ps
docker compose logs -f backend worker frontend
```

Остановка Docker-сервисов, включая инфраструктуру локального варианта:

```bash
docker compose down
```

Пользователи, роли, история и очередь сохраняются в именованных томах,
изображения — в `backend/app/static/uploads` и `backend/app/static/processed`.
Не добавляй `-v`, если нужны данные. У существующего тома PostgreSQL изменение
`DB_*` в `.env` не меняет уже созданные учётные данные БД.

Локальные API, worker и Vite останавливаются через `Ctrl+C` в соответствующих
терминалах. Выход из venv после остановки Python-процесса:

```bash
deactivate
```
