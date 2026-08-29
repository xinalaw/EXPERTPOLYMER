# Фронтенд: expert-polymer

Vue 3 + Vite. Интерфейс системы анализа полимерных порошков: регистрация и
вход, загрузка СЭМ-снимка, результаты анализа с заключением экспертной системы,
история исследований.

Часть объединённого проекта — общее описание в [корневом README](../README.md).

## Что где

```
src/
├── api/
│   ├── client.js       # базовый fetch-клиент, JWT, разбор ошибок API
│   ├── auth.js         # регистрация, вход, текущий пользователь
│   └── analysis.js     # /api/analyze, асинхронный анализ, история, WebSocket
├── components/
│   ├── AnalysisPage.vue          # загрузка снимка и результаты анализа
│   ├── AnalysisHistoryPage.vue   # история исследований
│   ├── LoginModal.vue RegisterModal.vue
│   └── MainPage.vue AboutPage.vue ContactsPage.vue NavBar.vue Footer.vue
└── App.vue
```

## Запуск

```bash
npm install
npm run dev
```

Открыть http://localhost:5173. Backend должен быть поднят на порту 8000 —
`vite.config.js` проксирует на него `/api` и `/static`, поэтому в режиме
разработки CORS не мешает.

## Сборка

```bash
npm run build
```

## Переменные окружения

Файл `.env`:

```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

Если оставить их пустыми, запросы пойдут на тот же origin — так собирают
сборку, которую раздаёт сам backend.

## Заключение экспертной системы

`AnalysisPage.vue` показывает блоки «Заключение экспертной системы», «Состав
порошка» и «Морфология». Данные для них приходят в `result_data` (поля
`expert`, `composition`, `size_stats`) и появляются, только когда backend
работает с реальным ядром. Если сервер запущен с `ML_BACKEND=mock`, вместо
вердикта выводится соответствующее пояснение.

## Устаревшее

`docs/legacy/` — документация и код первой версии, когда фронтенд ходил в
собственный Express-сервер и напрямую в PostgreSQL. Сейчас не используется.
