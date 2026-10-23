# Контекст сборки — корень репозитория. По умолчанию собирается полный ML-образ.
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/srv

WORKDIR /srv

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Ядро экспертной системы и веса модели
COPY pyproject.toml cli.py ./
COPY expert_system ./expert_system
COPY data/models ./data/models

# Веб-часть
COPY backend ./backend

# app/static и alembic.ini адресуются относительно рабочей директории
WORKDIR /srv/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Лёгкий backend/worker: API, очередь и mock-анализ без torch/ultralytics.
FROM base AS runtime

# Frontend собирается отдельно; npm ci повторяется только при смене lock-файла.
FROM node:22-alpine AS frontend

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend ./

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173", "--strictPort"]

# CPU torch ставится первым, чтобы ultralytics не подтягивал CUDA-колёса.
# Последний target сохраняет полный ML-режим для обычного docker build.
FROM base AS ml

RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch torchvision
RUN pip install --no-cache-dir -r /srv/requirements-ml.txt
