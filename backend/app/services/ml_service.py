"""
Адаптер между веб-частью (FastAPI + Celery) и ядром экспертной системы.

До объединения проектов здесь была заглушка: на изображении рисовался один
прямоугольник "Mock particle". Теперь вызывается настоящий конвейер из пакета
``expert_system``: сегментация частиц YOLOv8-seg -> морфологические метрики ->
нечёткий вывод Mamdani -> вердикт о пригодности порошка.

Выбор реализации задаёт переменная окружения ``ML_BACKEND``:

    auto (по умолчанию) - экспертная система, если она импортируется и найден
                          файл модели; иначе заглушка;
    expert_system       - только экспертная система (ошибка, если недоступна);
    mock                - только заглушка (используется в тестах и CI, где
                          не нужны гигабайты весов torch).

Публичный контракт функции ``analysis_material_image`` не изменился, поэтому
контроллер и Celery-задача остались прежними.
"""
from __future__ import annotations

import logging
import os
import shutil
import sys
import threading
import time
from pathlib import Path

import cv2
from dotenv import load_dotenv

# Модуль может вызываться и вне FastAPI/Celery (например, из скриптов),
# поэтому .env подхватывается здесь же. Уже установленные переменные
# окружения имеют приоритет — на этом держится ML_BACKEND=mock в тестах.
load_dotenv()

logger = logging.getLogger(__name__)

# Корень объединённого проекта: backend/app/services/ml_service.py -> ../../..
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Ядро лежит рядом с backend/, а не внутри него. Если пакет не установлен
# через `pip install -e .`, добавляем корень проекта в путь импорта.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MOCK_MODEL_INFO = {
    "name": "mock_cnn_module",
    "version": "0.1.0",
    "type": "mock",
}

_analyzer = None
_analyzer_lock = threading.Lock()


# ---------------------------------------------------------------------------
#  Выбор реализации
# ---------------------------------------------------------------------------

def _expert_system_available() -> tuple[bool, str]:
    """Готово ли ядро к работе: импортируется ли пакет и есть ли веса модели."""
    try:
        from expert_system import config
    except ImportError as error:
        return False, f"пакет expert_system недоступен: {error}"

    if not Path(config.MODEL_PATH).exists():
        return False, f"файл модели не найден: {config.MODEL_PATH}"

    return True, ""


def resolve_ml_backend() -> str:
    """Возвращает фактическую реализацию: 'expert_system' или 'mock'."""
    requested = os.getenv("ML_BACKEND", "auto").strip().lower()

    if requested == "mock":
        return "mock"

    available, reason = _expert_system_available()

    if requested == "expert_system":
        if not available:
            raise RuntimeError(
                "ML_BACKEND=expert_system, но экспертная система недоступна: "
                f"{reason}"
            )
        return "expert_system"

    if requested not in ("auto", ""):
        logger.warning(
            "Неизвестное значение ML_BACKEND=%r, используется auto", requested
        )

    if available:
        return "expert_system"

    logger.warning(
        "Экспертная система недоступна (%s) - используется заглушка", reason
    )
    return "mock"


def get_analyzer():
    """Ленивая инициализация Analyzer: веса YOLO грузятся один раз на процесс."""
    global _analyzer

    if _analyzer is None:
        with _analyzer_lock:
            if _analyzer is None:
                from expert_system import Analyzer

                logger.info("Загрузка модели экспертной системы...")
                _analyzer = Analyzer()

    return _analyzer


# ---------------------------------------------------------------------------
#  Преобразование результата ядра в формат API
# ---------------------------------------------------------------------------

def build_result_data(
    analysis: dict,
    width: int,
    height: int,
    processing_time_ms: float,
) -> dict:
    """
    Приводит результат ``Analyzer.analyze()`` к структуре ``result_data`` API.

    Чистая функция: не обращается ни к модели, ни к файловой системе, поэтому
    покрывается тестами без установленных весов YOLO.
    """
    from expert_system import __version__ as core_version

    particles = analysis.get("particles", [])

    detections = [
        {
            "label": particle["class"],
            "confidence": particle["confidence"],
            "bbox": {
                "x1": particle["bbox"][0],
                "y1": particle["bbox"][1],
                "x2": particle["bbox"][0] + particle["bbox"][2],
                "y2": particle["bbox"][1] + particle["bbox"][3],
            },
            "circularity": particle.get("circularity"),
            "diameter_px": particle.get("diameter"),
            "area_px": particle.get("area"),
        }
        for particle in particles
    ]

    return {
        "image": {"width": width, "height": height},
        "detections": detections,
        "particles_detected": analysis.get("total_particles", len(particles)),
        "model": {
            "name": "yolo_particles_seg",
            "version": core_version,
            "type": "yolov8-seg+fuzzy",
        },
        "processing_time_ms": processing_time_ms,
        # Расширение относительно заглушки - данные экспертной системы
        "composition": analysis.get("composition"),
        "avg_circularity": analysis.get("avg_circularity"),
        "dispersity": analysis.get("dispersity"),
        "size_stats": analysis.get("size_stats"),
        "expert": analysis.get("expert"),
    }


def _mean_confidence(analysis: dict) -> float:
    """Средняя уверенность модели по всем найденным частицам."""
    particles = analysis.get("particles", [])

    if not particles:
        return 0.0

    return round(sum(p["confidence"] for p in particles) / len(particles), 3)


# ---------------------------------------------------------------------------
#  Реализации
# ---------------------------------------------------------------------------

def _analyze_with_expert_system(
    original_file_path: str,
    processed_file_path: str,
) -> dict:
    """Полный конвейер: сегментация -> метрики -> нечёткий вывод -> визуализация."""
    from expert_system import visualization

    start_time = time.perf_counter()

    image = cv2.imread(original_file_path)

    if image is None:
        raise ValueError("Не удалось обработать изображение.")

    height, width = image.shape[:2]

    analysis = get_analyzer().analyze(original_file_path)

    # Частицы не найдены - это валидный результат анализа, а не ошибка
    if analysis.get("total_particles", 0) == 0:
        shutil.copyfile(original_file_path, processed_file_path)

        processing_time_ms = (time.perf_counter() - start_time) * 1000

        return {
            "result": "Частицы не обнаружены",
            "confidence": 0.0,
            "width": width,
            "height": height,
            "result_data": build_result_data(
                {"total_particles": 0, "particles": []},
                width,
                height,
                processing_time_ms,
            ),
        }

    expert = analysis["expert"]

    visualization.draw_particles(
        image_path=original_file_path,
        particles=analysis["particles"],
        output_path=processed_file_path,
        title=f"{expert['verdict']}: {expert['score']}/100",
        legend=False,
    )

    processing_time_ms = (time.perf_counter() - start_time) * 1000

    return {
        "result": (
            f"{expert['conclusion']}. "
            f"Оценка пригодности {expert['score']}/100, "
            f"частиц обнаружено: {analysis['total_particles']}"
        ),
        "confidence": _mean_confidence(analysis),
        "width": width,
        "height": height,
        "result_data": build_result_data(
            analysis,
            width,
            height,
            processing_time_ms,
        ),
    }


def _analyze_with_mock(
    original_file_path: str,
    processed_file_path: str,
) -> dict:
    """Заглушка: один прямоугольник по центру. Нужна тестам и CI без весов модели."""
    start_time = time.perf_counter()

    image = cv2.imread(original_file_path)

    if image is None:
        raise ValueError("Не удалось обработать изображение.")

    height, width = image.shape[:2]

    x1 = int(width * 0.25)
    y1 = int(height * 0.25)
    x2 = int(width * 0.75)
    y2 = int(height * 0.75)

    confidence = 0.95

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv2.putText(
        image,
        "Mock particle",
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_COMPLEX,
        0.8,
        (0, 255, 0),
        2,
    )

    cv2.imwrite(processed_file_path, image)

    processing_time_ms = (time.perf_counter() - start_time) * 1000

    result_data = {
        "image": {
            "width": width,
            "height": height,
        },
        "detections": [
            {
                "label": "particle",
                "confidence": confidence,
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                },
            }
        ],
        "particles_detected": 1,
        "model": dict(MOCK_MODEL_INFO),
        "processing_time_ms": processing_time_ms,
    }

    return {
        "result": "Изображение обработано. Найдены частицы",
        "confidence": confidence,
        "width": width,
        "height": height,
        "result_data": result_data,
    }


# ---------------------------------------------------------------------------
#  Точка входа для контроллера и Celery-задачи
# ---------------------------------------------------------------------------

def analysis_material_image(
    original_file_path: str,
    processed_file_path: str,
) -> dict:
    """
    Анализ одного изображения материала.

    Возвращает словарь с ключами result, confidence, width, height, result_data.
    """
    backend = resolve_ml_backend()

    if backend == "expert_system":
        try:
            return _analyze_with_expert_system(
                original_file_path=original_file_path,
                processed_file_path=processed_file_path,
            )
        except ValueError:
            # Битое или нечитаемое изображение - ошибка входных данных,
            # заглушка её не исправит
            raise
        except Exception as error:
            if os.getenv("ML_STRICT", "").strip().lower() in ("1", "true", "yes"):
                raise

            logger.exception(
                "Ошибка экспертной системы, откат на заглушку: %s", error
            )

    return _analyze_with_mock(
        original_file_path=original_file_path,
        processed_file_path=processed_file_path,
    )
