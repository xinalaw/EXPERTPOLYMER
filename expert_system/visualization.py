"""
Визуализация результатов детекции: bounding boxes и маски сегментации.

Вынесена в отдельный модуль, чтобы детектор отвечал только за инференс
(принцип единственной ответственности). Функции принимают готовый
YOLODetector и сами выполняют инференс на указанном изображении.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import cv2
import numpy as np

from . import config

if TYPE_CHECKING:  # импорт только для аннотаций — не тянет ultralytics
    from .detector import YOLODetector


def draw_boxes(detector: YOLODetector, image_path: str, output_path: str) -> str:
    """Сохраняет изображение с bounding boxes, классами и уверенностью."""
    results = detector.predict(image_path)
    img = cv2.imread(image_path)

    for i in range(len(results.boxes)):
        cls_id = int(results.boxes.cls[i])
        confidence = float(results.boxes.conf[i])
        class_name = detector.classes[cls_id]
        color = config.CLASS_COLORS[class_name]

        x1, y1, x2, y2 = map(int, results.boxes.xyxy[i])
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

        label = f"{class_name} {confidence:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(img, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    cv2.imwrite(output_path, img)
    return output_path


def draw_masks(detector: YOLODetector, image_path: str, output_path: str) -> str:
    """Сохраняет изображение с полупрозрачными масками сегментации и легендой."""
    results = detector.predict(image_path)
    img = cv2.imread(image_path)

    if results.masks is None:
        cv2.imwrite(output_path, img)
        return output_path

    overlay = img.copy()
    orig_h, orig_w = results.orig_shape

    for i in range(len(results.boxes)):
        cls_id = int(results.boxes.cls[i])
        class_name = detector.classes[cls_id]
        color = config.CLASS_COLORS[class_name]

        mask = results.masks.data[i].cpu().numpy()
        mask = (mask > 0.5).astype(np.uint8)
        mask = cv2.resize(mask, (orig_w, orig_h),
                          interpolation=cv2.INTER_NEAREST)

        overlay[mask == 1] = color
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img, contours, -1, color, 2)

    # Смешиваем оригинал с цветными масками (прозрачность 40 %)
    img = cv2.addWeighted(overlay, 0.4, img, 0.6, 0)

    # Легенда
    for j, (name, color) in enumerate(config.CLASS_COLORS.items()):
        y = 20 + j * 22
        cv2.rectangle(img, (8, y - 12), (22, y + 2), color, -1)
        cv2.putText(img, name, (26, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imwrite(output_path, img)
    return output_path


def draw_particles(image_path: str, particles: list[dict], output_path: str,
                   title: str | None = None, legend: bool = True) -> str:
    """
    Отрисовка уже посчитанных частиц — без повторного инференса.

    В отличие от draw_boxes/draw_masks, которые сами вызывают модель,
    эта функция работает по готовому списку из Analyzer.analyze()
    (ключ "particles"). Нужна веб-части: один прогон модели на запрос
    вместо трёх.

    particles — элементы вида {"class", "confidence", "bbox": [x, y, w, h]}.
    title     — необязательная подпись снизу (например, вердикт эксперта);
    legend    — рисовать ли список классов в углу. На мелких изображениях
                легенда перекрывает частицы и дублирует подписи рамок,
                поэтому веб-часть отключает её.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Не удалось прочитать изображение: {image_path}")

    for particle in particles:
        class_name = particle["class"]
        color = config.CLASS_COLORS.get(class_name, (200, 200, 200))
        x, y, w, h = particle["bbox"]

        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

        label = f"{class_name} {particle['confidence']:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        label_y = y if y - th - 4 > 0 else y + h + th + 4
        cv2.rectangle(img, (x, label_y - th - 4), (x + tw + 4, label_y), color, -1)
        cv2.putText(img, label, (x + 2, label_y - 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

    # Легенда — только по классам, реально встретившимся на изображении
    present = [c for c in config.CLASSES
               if any(p["class"] == c for p in particles)] if legend else []
    for j, name in enumerate(present):
        y = 20 + j * 22
        cv2.rectangle(img, (8, y - 12), (22, y + 2), config.CLASS_COLORS[name], -1)
        cv2.putText(img, name, (26, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if title:
        h_img = img.shape[0]
        cv2.putText(img, title, (8, h_img - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
        cv2.putText(img, title, (8, h_img - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imwrite(output_path, img)
    return output_path
