"""
Расчёт морфологических характеристик частиц.

Все функции — чистые (без состояния и побочных эффектов), что позволяет
покрыть их модульными тестами и привести формулы в пояснительной записке.

Используемые показатели:
    * Округлость (circularity):  C = 4·π·S / P²,
      где S — площадь контура, P — периметр. C = 1 для идеального круга.
    * Эквивалентный диаметр:     d = sqrt(4·S / π) —
      диаметр круга той же площади, что и частица.
    * Дисперсность (коэффициент вариации размеров): CV = σ(d) / mean(d),
      обрезается до 1.0. Чем ниже, тем однороднее порошок по размеру.
"""
from __future__ import annotations

import cv2
import numpy as np


def circularity(contour: np.ndarray) -> float:
    """Округлость контура: 4·π·S / P². Возвращает значение в [0, 1]."""
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, closed=True)
    if perimeter <= 0:
        return 0.0
    value = (4.0 * np.pi * area) / (perimeter ** 2)
    # Из-за дискретизации контура значение может чуть превышать 1
    return float(min(value, 1.0))


def equivalent_diameter(area: float) -> float:
    """Эквивалентный диаметр круга той же площади, px."""
    if area <= 0:
        return 0.0
    return float(np.sqrt(4.0 * area / np.pi))


def dispersity(diameters: list[float]) -> float:
    """
    Коэффициент вариации диаметров (мера полидисперсности), в [0, 1].

    0 — все частицы одного размера, 1 — крайне неоднородный порошок.
    Для выборки из менее чем двух частиц определяется как 0.
    """
    if len(diameters) < 2:
        return 0.0
    mean = float(np.mean(diameters))
    if mean == 0:
        return 0.0
    return float(min(np.std(diameters) / mean, 1.0))


def size_statistics(diameters: list[float]) -> dict:
    """Сводная статистика размеров частиц (в пикселях)."""
    if not diameters:
        return {"min_px": 0.0, "max_px": 0.0, "mean_px": 0.0, "std_px": 0.0}
    return {
        "min_px":  round(float(np.min(diameters)), 1),
        "max_px":  round(float(np.max(diameters)), 1),
        "mean_px": round(float(np.mean(diameters)), 1),
        "std_px":  round(float(np.std(diameters)), 1),
    }


def largest_contour(mask: np.ndarray) -> np.ndarray | None:
    """Наибольший внешний контур бинарной маски (или None, если контуров нет)."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)
