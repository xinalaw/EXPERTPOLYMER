"""
Модуль детекции и сегментации частиц на СЭМ-изображениях.

Отвечает только за работу с нейросетевой моделью YOLOv8-seg:
запуск инференса и преобразование «сырых» результатов в список частиц
с морфологическими характеристиками. Визуализация вынесена в visualization.py.
"""
from __future__ import annotations

import os

import cv2
import numpy as np
from ultralytics import YOLO

from . import config, metrics


class YOLODetector:
    """Обёртка над моделью YOLOv8-seg для сегментации частиц порошка."""

    def __init__(self, model_path: str | os.PathLike = config.MODEL_PATH,
                 confidence: float = config.CONFIDENCE_THRESHOLD):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Модель не найдена: {model_path}")
        self.model = YOLO(str(model_path))
        self.classes = config.CLASSES
        self.confidence = confidence

    def predict(self, image_path: str):
        """Запуск инференса. Возвращает «сырой» объект Results ultralytics."""
        return self.model(image_path, conf=self.confidence, verbose=False)[0]

    def detect(self, image_path: str) -> dict:
        """
        Детекция частиц с расчётом характеристик каждой из них.

        Возвращает словарь:
            particles — список частиц (класс, уверенность, округлость,
                        эквивалентный диаметр, площадь, bbox);
            total     — общее число частиц.
        """
        results = self.predict(image_path)

        if results.masks is None:
            return {"particles": [], "total": 0}

        orig_h, orig_w = results.orig_shape
        particles = []

        for i in range(len(results.boxes)):
            cls_id = int(results.boxes.cls[i])
            confidence = float(results.boxes.conf[i])
            class_name = self.classes[cls_id]

            # Маска экземпляра -> бинарная маска в исходном разрешении
            mask = results.masks.data[i].cpu().numpy()
            mask = (mask > 0.5).astype(np.uint8) * 255
            mask = cv2.resize(mask, (orig_w, orig_h),
                              interpolation=cv2.INTER_NEAREST)

            contour = metrics.largest_contour(mask)
            if contour is None:
                continue

            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)

            particles.append({
                "class":       class_name,
                "confidence":  round(confidence, 3),
                "circularity": round(metrics.circularity(contour), 3),
                "diameter":    round(metrics.equivalent_diameter(area), 1),
                "area":        round(float(area), 1),
                "bbox":        [int(x), int(y), int(w), int(h)],
            })

        return {"particles": particles, "total": len(particles)}
