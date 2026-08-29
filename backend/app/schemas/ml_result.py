"""
Схемы результата анализа изображения.

Базовая часть (image / detections / model) осталась от версии с заглушкой —
на неё опирается фронтенд. Блоки composition, size_stats и expert добавлены
после подключения ядра экспертной системы; они необязательны, поэтому старые
записи в базе и режим ML_BACKEND=mock продолжают валидироваться.
"""
from pydantic import BaseModel


class BoundingBoxesSchema(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class DetectionSchema(BaseModel):
    label: str
    confidence: float
    bbox: BoundingBoxesSchema

    # Морфология частицы — заполняется только экспертной системой
    circularity: float | None = None
    diameter_px: float | None = None
    area_px: float | None = None


class ImageInfoSchema(BaseModel):
    height: int
    width: int


class ModelInfoSchema(BaseModel):
    name: str
    version: str
    type: str


class SizeStatsSchema(BaseModel):
    """Статистика эквивалентных диаметров частиц, в пикселях."""

    min_px: float
    max_px: float
    mean_px: float
    std_px: float


class ExpertInputsSchema(BaseModel):
    """Входы нечёткой системы, все в диапазоне [0, 1]."""

    sphericity: float
    smoothness: float
    uniformity: float


class ExpertVerdictSchema(BaseModel):
    """Заключение нечёткой экспертной подсистемы (Mamdani)."""

    score: float
    verdict: str
    conclusion: str
    inputs: ExpertInputsSchema


class MLResultDataSchema(BaseModel):
    image: ImageInfoSchema
    detections: list[DetectionSchema]
    particles_detected: int
    model: ModelInfoSchema
    processing_time_ms: float

    # Результаты экспертной системы (отсутствуют в режиме mock)
    composition: dict[str, float] | None = None
    avg_circularity: float | None = None
    dispersity: float | None = None
    size_stats: SizeStatsSchema | None = None
    expert: ExpertVerdictSchema | None = None
