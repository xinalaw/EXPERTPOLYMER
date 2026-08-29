"""Модульные тесты расчёта морфологических характеристик (metrics.py)."""
import math

import cv2
import numpy as np
import pytest

from expert_system import metrics


def make_circle_contour(radius=50):
    """Контур идеального круга на синтетической маске."""
    mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.circle(mask, (100, 100), radius, 255, -1)
    return metrics.largest_contour(mask)


def make_square_contour(side=80):
    mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.rectangle(mask, (60, 60), (60 + side, 60 + side), 255, -1)
    return metrics.largest_contour(mask)


class TestCircularity:
    def test_circle_is_close_to_one(self):
        # Из-за растеризации периметр дискретного круга завышен,
        # поэтому округлость ~0.89, а не ровно 1.0
        c = metrics.circularity(make_circle_contour())
        assert c > 0.85

    def test_square_is_less_than_circle(self):
        square = metrics.circularity(make_square_contour())
        circle = metrics.circularity(make_circle_contour())
        assert square < circle

    def test_never_exceeds_one(self):
        assert metrics.circularity(make_circle_contour(radius=5)) <= 1.0


class TestEquivalentDiameter:
    def test_known_area(self):
        # Площадь круга диаметром 10: pi * 25
        area = math.pi * 25
        assert metrics.equivalent_diameter(area) == pytest.approx(10.0)

    def test_zero_area(self):
        assert metrics.equivalent_diameter(0) == 0.0


class TestDispersity:
    def test_identical_sizes_give_zero(self):
        assert metrics.dispersity([10.0, 10.0, 10.0]) == 0.0

    def test_single_particle_is_zero(self):
        assert metrics.dispersity([42.0]) == 0.0

    def test_clipped_at_one(self):
        assert metrics.dispersity([0.1, 1000.0]) <= 1.0

    def test_more_spread_means_higher_value(self):
        narrow = metrics.dispersity([9, 10, 11])
        wide = metrics.dispersity([2, 10, 18])
        assert wide > narrow


class TestSizeStatistics:
    def test_empty(self):
        stats = metrics.size_statistics([])
        assert stats["mean_px"] == 0.0

    def test_basic(self):
        stats = metrics.size_statistics([10.0, 20.0])
        assert stats["min_px"] == 10.0
        assert stats["max_px"] == 20.0
        assert stats["mean_px"] == 15.0
