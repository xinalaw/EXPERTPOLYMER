# Ядро: экспертная система анализа морфологии частиц

Документация пакета `expert_system` — той части объединённого проекта, которая
и выполняет анализ. Общее описание системы и запуск веб-стека —
в [корневом README](../README.md).

Ядро определяет пригодность полимерного порошка для аддитивного производства
по СЭМ-изображению: сегментирует частицы нейросетью YOLOv8-seg, рассчитывает
морфологические характеристики и выносит заключение методом нечёткого логического
вывода (Mamdani).

Пакет автономен: не зависит ни от FastAPI, ни от базы данных веб-части.
Используется в двух режимах — из CLI (`python cli.py`) и из backend'а
(`backend/app/services/ml_service.py`).

## Архитектура

```
СЭМ-изображение
      │
      ▼
┌─────────────────┐   список частиц    ┌─────────────────┐
│   detector.py   │ ─────────────────▶ │   metrics.py    │
│  (YOLOv8-seg)   │   (класс, маска)   │ округлость,     │
└─────────────────┘                    │ диаметр,        │
                                       │ дисперсность    │
                                       └────────┬────────┘
                                                │ sphericity, smoothness,
                                                │ uniformity ∈ [0, 1]
                                                ▼
┌─────────────────┐    score, вердикт  ┌─────────────────┐
│   storage.py    │ ◀───────────────── │ fuzzy_expert.py │
│   (SQLite)      │                    │ нечёткий вывод  │
└─────────────────┘                    │   (Mamdani)     │
                                       └─────────────────┘

Все этапы объединяет фасад analyzer.py (класс Analyzer).
```

## Структура проекта

```
<корень проекта>/
├── expert_system/            # ядро системы (Python-пакет)
│   ├── config.py             # все константы: классы, пути, пороги
│   ├── detector.py           # сегментация частиц (YOLOv8-seg)
│   ├── metrics.py            # морфологические характеристики (чистые функции)
│   ├── fuzzy_expert.py       # нечёткая экспертная подсистема
│   ├── analyzer.py           # фасад: полный конвейер анализа
│   ├── storage.py            # сохранение результатов (SQLite)
│   └── visualization.py      # отрисовка boxes и масок
├── cli.py                    # CLI — точка входа
├── tests/                    # модульные тесты (pytest)
├── examples/
│   └── api_example.py        # пример интеграции в веб-приложение
├── data/
│   ├── models/yolo_particles_seg.pt   # обученная модель
│   └── results/               # визуализации и JSON-результаты
└── requirements-ml.txt        # зависимости, включая ultralytics
```

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements-ml.txt
pip install -e .
```

Веса модели лежат в `data/models/yolo_particles_seg.pt`. Путь можно
переопределить переменной окружения `ES_MODEL_PATH`.

## Использование

### Из командной строки

```bash
# Анализ одного изображения
python cli.py path/to/image.png

# С визуализациями (сохраняются в data/results/)
python cli.py image.png --boxes --masks

# Анализ всей папки + выгрузка в JSON
python cli.py data/images/spherical/ --json results.json

# Без записи в базу данных
python cli.py image.png --no-db
```

### Как библиотека (для интеграции в сайт)

```python
from expert_system import Analyzer

analyzer = Analyzer()                       # загружается один раз
result = analyzer.analyze("image.png")      # dict с полным результатом

print(result["expert"]["score"])            # 0–100
print(result["expert"]["conclusion"])       # текстовое заключение
```

Готовый пример REST API на FastAPI — в `examples/api_example.py`.

## Методика

1. **Сегментация.** YOLOv8-seg выделяет каждую частицу и относит её к одному
   из 5 морфологических классов: dendritic, fragmented, spongy, spherical, teardrop.
2. **Морфологические характеристики** (по маске каждой частицы):
   - округлость `C = 4πS / P²` (1.0 — идеальный круг);
   - эквивалентный диаметр `d = √(4S/π)`;
   - дисперсность выборки — коэффициент вариации диаметров `σ(d)/mean(d)`.
3. **Нечёткий вывод.** Три входа в [0, 1]: доля сферических частиц (sphericity),
   средняя округлость (smoothness), однородность размеров `1 − дисперсность`
   (uniformity). База из 9 правил, треугольные функции принадлежности,
   дефаззификация методом центра тяжести. Выход — оценка пригодности 0–100:
   - ≥ 70 — пригоден;
   - 40–69 — условно пригоден;
   - < 40 — не пригоден.

## Тесты

```bash
pytest tests/ -v
```

## Выходной формат

```json
{
  "total_particles": 42,
  "composition": {"spherical": 65.0, "dendritic": 10.0, "...": "..."},
  "avg_circularity": 0.81,
  "dispersity": 0.27,
  "size_stats": {"min_px": 12.0, "max_px": 88.5, "mean_px": 41.2, "std_px": 11.3},
  "expert": {
    "score": 74.5,
    "verdict": "suitable",
    "conclusion": "Материал пригоден для аддитивного производства",
    "inputs": {"sphericity": 0.65, "smoothness": 0.81, "uniformity": 0.73}
  },
  "particles": [ {"class": "spherical", "circularity": 0.93, "...": "..."} ]
}
```

## Использование из веб-части

Backend вызывает ядро через `backend/app/services/ml_service.py`. Что делает
этот адаптер:

- держит один экземпляр `Analyzer` на процесс — веса YOLO грузятся однократно;
- переводит `bbox` из формата ядра `[x, y, w, h]` в `{x1, y1, x2, y2}`,
  который ожидает API и фронтенд;
- прокидывает в ответ `composition`, `size_stats` и блок `expert`;
- рисует processed-изображение функцией `visualization.draw_particles()` —
  она работает по уже посчитанному списку частиц и не запускает модель повторно
  (в отличие от `draw_boxes`/`draw_masks`, которые делают собственный инференс
  и нужны в CLI);
- при `ML_BACKEND=mock` полностью обходит ядро — это режим для CI и разработки
  фронтенда.

Отсутствие частиц на снимке (`total_particles == 0`) считается нормальным
результатом анализа, а не ошибкой: API вернёт `particles_detected: 0`
и `expert: null`.
