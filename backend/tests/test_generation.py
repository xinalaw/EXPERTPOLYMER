import base64
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.middleware.auth_middleware import get_current_user


def test_generation_requires_authentication():
    with TestClient(app) as client:
        assert client.post('/api/generate').status_code in (401, 403)


def test_generation_produces_analyzable_png():
    app.dependency_overrides[get_current_user] = lambda: object()
    try:
        with TestClient(app) as client:
            for _ in range(3):
                response = client.post('/api/generate')
                assert response.status_code == 200
                image = Image.open(BytesIO(base64.b64decode(response.json()['image'])))
                assert image.format == 'PNG'
                assert image.size == (224, 224)
                assert image.getextrema()[0] < image.getextrema()[1]
    finally:
        app.dependency_overrides.pop(get_current_user, None)
