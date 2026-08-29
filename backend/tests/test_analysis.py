from io import BytesIO

import cv2
import numpy as np


def register_user(
    client,
    first_name: str,
    last_name: str,
    email: str,
    password: str = "test12345",
):
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "organization": "KFU",
            "password": password,
            "password_confirm": password,
        },
    )

    assert response.status_code == 200
    return response.json()


def login_user(client, email: str, password: str = "test12345") -> str:
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def create_test_image_bytes():
    image = np.zeros((100, 100, 3), dtype=np.uint8)

    success, encoded_image = cv2.imencode(".png", image)

    assert success is True

    return BytesIO(encoded_image.tobytes())


def test_analyze_image_by_researcher(client):
    register_user(
        client,
        first_name="Researcher",
        last_name="User",
        email="researcher@example.com",
    )

    token = login_user(client, "researcher@example.com")

    response = client.post(
        "/api/analyze",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": ("test.png", create_test_image_bytes(), "image/png"),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] is not None
    assert data["image_path"].startswith("/static/uploads/")
    assert data["processed_image_path"].startswith("/static/processed/")
    assert data["result"] == "Изображение обработано. Найдены частицы"
    assert data["confidence"] == 0.95
    assert data["width"] == 100
    assert data["height"] == 100

    assert data["result_data"]["particles_detected"] == 1
    assert len(data["result_data"]["detections"]) == 1
    assert data["result_data"]["model"]["name"] == "mock_cnn_module"


def test_get_analysis_result(client):
    register_user(
        client,
        first_name="Researcher",
        last_name="Result",
        email="researcher_result@example.com",
    )

    token = login_user(client, "researcher_result@example.com")

    analyze_response = client.post(
        "/api/analyze",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": ("test.png", create_test_image_bytes(), "image/png"),
        },
    )

    analysis_id = analyze_response.json()["id"]

    response = client.get(
        f"/api/results/{analysis_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == analysis_id
    assert data["result_data"]["particles_detected"] == 1
