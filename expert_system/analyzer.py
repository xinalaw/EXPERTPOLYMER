
from __future__ import annotations

import numpy as np

from . import config, metrics
from .detector import YOLODetector
from .fuzzy_expert import FuzzyExpert


class Analyzer:
    """Полный конвейер анализа СЭМ-изображения порошка."""

    def __init__(self, model_path=config.MODEL_PATH):
        self.detector = YOLODetector(model_path)
        self.fuzzy = FuzzyExpert()

    def analyze(self, image_path: str) -> dict:
        """
        Анализ одного изображения.

        Возвращает словарь с составом порошка по классам, морфологическими
        показателями, статистикой размеров и заключением экспертной системы.
        """
        # 1. Детекция и сегментация всех частиц
        detection = self.detector.detect(image_path)
        particles = detection["particles"]
        total = detection["total"]

        if total == 0:
            return {"error": "Частицы не обнаружены", "total_particles": 0}

        # 2. Состав по классам, % от общего числа частиц
        counts = {c: 0 for c in config.CLASSES}
        for p in particles:
            counts[p["class"]] += 1
        composition = {k: round(v / total * 100, 1) for k, v in counts.items()}

        # 3. Морфологические показатели выборки
        avg_circularity = float(np.mean([p["circularity"] for p in particles]))
        diameters = [p["diameter"] for p in particles]
        disp = metrics.dispersity(diameters)

        # 4. Входы нечёткой системы (все в [0, 1])
        sphericity = composition["spherical"] / 100   # доля сферических частиц
        smoothness = avg_circularity                  # средняя округлость
        uniformity = 1.0 - disp                       # однородность размеров

        # 5. Нечёткий экспертный вывод
        expert = self.fuzzy.evaluate(sphericity, smoothness, uniformity)

        return {
            "total_particles": total,
            "composition":     composition,
            "avg_circularity": round(avg_circularity, 3),
            "dispersity":      round(disp, 3),
            "size_stats":      metrics.size_statistics(diameters),
            "expert":          expert,
            "particles":       particles,
        }
