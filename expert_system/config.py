"""
Конфигурация экспертной системы.

Единый источник всех констант: классы частиц, пути, пороги.

Все пути можно переопределить переменными окружения — это нужно потому,
что после объединения проектов ядро используется в двух режимах:

    * локально из CLI      — пути считаются от корня репозитория;
    * внутри backend/Docker — пути задаются через ES_MODEL_PATH и др.
"""
import os
from pathlib import Path

# Корень объединённого проекта (папка, где лежат expert_system/, backend/, data/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _path_from_env(var: str, default: Path) -> Path:
    """Путь из переменной окружения, иначе значение по умолчанию."""
    value = os.getenv(var)
    return Path(value).expanduser().resolve() if value else default


# Классы частиц (порядок должен совпадать с порядком классов при обучении YOLO!)
CLASSES = ["dendritic", "fragmented", "spongy", "spherical", "teardrop"]

# Человекочитаемые названия классов (для отчётов и веб-интерфейса)
CLASS_LABELS_RU = {
    "dendritic":  "дендритные",
    "fragmented": "осколочные",
    "spongy":     "губчатые",
    "spherical":  "сферические",
    "teardrop":   "каплевидные",
}

# Цвета классов для визуализации (BGR, формат OpenCV)
CLASS_COLORS = {
    "dendritic":  (255, 100, 100),
    "fragmented": (100, 100, 255),
    "spongy":     (100, 255, 100),
    "spherical":  (255, 255, 100),
    "teardrop":   (255, 100, 255),
}

# Модель
MODEL_PATH = _path_from_env(
    "ES_MODEL_PATH",
    PROJECT_ROOT / "data" / "models" / "yolo_particles_seg.pt",
)
CONFIDENCE_THRESHOLD = float(os.getenv("ES_CONFIDENCE_THRESHOLD", "0.25"))

# База данных ядра (используется только CLI-режимом;
# backend хранит результаты в своей PostgreSQL)
DATABASE_URL = os.getenv(
    "ES_DATABASE_URL",
    f"sqlite:///{PROJECT_ROOT / 'expert_system.db'}",
)

# Папка для результатов (визуализации, JSON)
RESULTS_DIR = _path_from_env("ES_RESULTS_DIR", PROJECT_ROOT / "data" / "results")

# Пороги итоговой оценки нечёткой системы
SCORE_SUITABLE = 70      # >= 70 — пригоден
SCORE_CONDITIONAL = 40   # >= 40 — условно пригоден

# Поддерживаемые форматы изображений
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
