"""
Тесты стыковки веб-части с ядром экспертной системы.

Веса YOLO здесь не нужны: проверяется выбор реализации, отображение результата
``Analyzer.analyze()`` в структуру API и то, что расширенные поля (вердикт
эксперта, состав порошка) проходят валидацию pydantic и не отсекаются
при сериализации ответа.
"""
import os

import pytest

from app.schemas.ml_result import MLResultDataSchema
from app.services import ml_service


# Результат Analyzer.analyze() — ровно в том виде, в каком его отдаёт ядро
ANALYZER_OUTPUT = {
    "total_particles": 2,
    "composition": {
        "dendritic": 0.0,
        "fragmented": 50.0,
        "spongy": 0.0,
        "spherical": 50.0,
        "teardrop": 0.0,
    },
    "avg_circularity": 0.751,
    "dispersity": 0.204,
    "size_stats": {
        "min_px": 20.0,
        "max_px": 30.0,
        "mean_px": 25.0,
        "std_px": 5.0,
    },
    "expert": {
        "score": 48.31,
        "verdict": "conditional",
        "conclusion": "Материал условно пригоден, требует дополнительной обработки",
        "inputs": {
            "sphericity": 0.5,
            "smoothness": 0.751,
            "uniformity": 0.796,
        },
    },
    "particles": [
        {
            "class": "spherical",
            "confidence": 0.97,
            "circularity": 0.88,
            "diameter": 30.0,
            "area": 706.9,
            "bbox": [10, 20, 30, 40],
        },
        {
            "class": "fragmented",
            "confidence": 0.81,
            "circularity": 0.62,
            "diameter": 20.0,
            "area": 314.2,
            "bbox": [100, 110, 25, 25],
        },
    ],
}


class TestResolveMlBackend:

    def test_mock_is_forced_by_env(self, monkeypatch):
        monkeypatch.setenv("ML_BACKEND", "mock")

        assert ml_service.resolve_ml_backend() == "mock"

    def test_unavailable_core_falls_back_to_mock(self, monkeypatch):
        monkeypatch.setenv("ML_BACKEND", "auto")
        monkeypatch.setattr(
            ml_service,
            "_expert_system_available",
            lambda: (False, "веса модели не найдены"),
        )

        assert ml_service.resolve_ml_backend() == "mock"

    def test_explicit_core_request_fails_loudly(self, monkeypatch):
        monkeypatch.setenv("ML_BACKEND", "expert_system")
        monkeypatch.setattr(
            ml_service,
            "_expert_system_available",
            lambda: (False, "веса модели не найдены"),
        )

        with pytest.raises(RuntimeError, match="экспертная система недоступна"):
            ml_service.resolve_ml_backend()


class TestBuildResultData:

    @pytest.fixture()
    def result_data(self):
        return ml_service.build_result_data(
            ANALYZER_OUTPUT,
            width=224,
            height=224,
            processing_time_ms=1234.5,
        )

    def test_bbox_converted_from_xywh_to_corners(self, result_data):
        first = result_data["detections"][0]

        # bbox ядра [x, y, w, h] = [10, 20, 30, 40]
        assert first["bbox"] == {"x1": 10, "y1": 20, "x2": 40, "y2": 60}

    def test_particle_class_becomes_detection_label(self, result_data):
        labels = [d["label"] for d in result_data["detections"]]

        assert labels == ["spherical", "fragmented"]

    def test_morphology_is_carried_into_detection(self, result_data):
        first = result_data["detections"][0]

        assert first["circularity"] == 0.88
        assert first["diameter_px"] == 30.0
        assert first["area_px"] == 706.9

    def test_expert_verdict_is_preserved(self, result_data):
        assert result_data["expert"]["verdict"] == "conditional"
        assert result_data["expert"]["score"] == 48.31
        assert result_data["composition"]["spherical"] == 50.0
        assert result_data["dispersity"] == 0.204

    def test_model_info_reports_real_pipeline(self, result_data):
        assert result_data["model"]["name"] == "yolo_particles_seg"
        assert result_data["model"]["type"] == "yolov8-seg+fuzzy"

    def test_empty_analysis_gives_zero_particles(self):
        result_data = ml_service.build_result_data(
            {"total_particles": 0, "particles": []},
            width=100,
            height=100,
            processing_time_ms=1.0,
        )

        assert result_data["particles_detected"] == 0
        assert result_data["detections"] == []
        assert result_data["expert"] is None

    def test_schema_accepts_expert_system_payload(self, result_data):
        """Ключевая проверка: расширенные поля не теряются при сериализации."""
        validated = MLResultDataSchema.model_validate(result_data)
        dumped = validated.model_dump()

        assert dumped["expert"]["verdict"] == "conditional"
        assert dumped["size_stats"]["mean_px"] == 25.0
        assert dumped["detections"][0]["diameter_px"] == 30.0

    def test_schema_still_accepts_mock_payload(self, tmp_path):
        """Старый формат заглушки остаётся валидным — без миграции данных."""
        image_path = tmp_path / "img.png"
        processed_path = tmp_path / "processed.png"

        import cv2
        import numpy as np

        cv2.imwrite(str(image_path), np.zeros((40, 60, 3), dtype=np.uint8))

        os.environ["ML_BACKEND"] = "mock"
        analysis = ml_service.analysis_material_image(
            original_file_path=str(image_path),
            processed_file_path=str(processed_path),
        )

        validated = MLResultDataSchema.model_validate(analysis["result_data"])

        assert validated.model.name == "mock_cnn_module"
        assert validated.expert is None
        assert analysis["width"] == 60
        assert analysis["height"] == 40
        assert processed_path.exists()


class TestMeanConfidence:

    def test_average_over_particles(self):
        assert ml_service._mean_confidence(ANALYZER_OUTPUT) == 0.89

    def test_no_particles_gives_zero(self):
        assert ml_service._mean_confidence({"particles": []}) == 0.0
