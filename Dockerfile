# Образ backend'а объединённого проекта.
#
# Контекст сборки — корень репозитория, а не backend/: внутрь нужно положить
# и веб-часть, и ядро экспертной системы с весами модели.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/srv

WORKDIR /srv

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# CPU-сборка torch ставится первой: иначе ultralytics подтянет CUDA-колёса
# и образ вырастет с ~1.5 ГБ до ~6 ГБ.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch torchvision

COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements-ml.txt

# Ядро экспертной системы и веса модели
COPY pyproject.toml cli.py ./
COPY expert_system ./expert_system
COPY data/models ./data/models

# Веб-часть
COPY backend ./backend

# app/static и alembic.ini адресуются относительно рабочей директории
WORKDIR /srv/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
