"""
ПРИМЕР интеграции экспертной системы в веб-приложение (FastAPI).

ВНИМАНИЕ: это не рабочий сервер проекта. После объединения кодовых баз
настоящая веб-часть живёт в backend/, а подключение ядра сделано в
backend/app/services/ml_service.py — там же авторизация, роли, очереди
и хранение результатов в PostgreSQL.

Файл оставлен как минимальный самодостаточный пример на 100 строк: он
показывает, как встроить пакет expert_system в стороннее приложение.
Запуск (из корня проекта):

    uvicorn examples.api_example:app --reload
"""
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from expert_system import Analyzer, config, storage, visualization

app = FastAPI(title="Expert System — Polymer Particles")

UPLOAD_DIR = config.PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

analyzer = Analyzer()
storage.init_db()


def _save_upload(file: UploadFile) -> Path:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in config.IMAGE_EXTENSIONS:
        raise HTTPException(400, "Поддерживаются только изображения")
    path = UPLOAD_DIR / f"{uuid.uuid4()}{suffix}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    path = _save_upload(file)
    try:
        result = analyzer.analyze(str(path))
        if "error" not in result:
            storage.save_result(result, str(path))
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/visualize/boxes")
async def visualize_boxes(file: UploadFile = File(...)):
    path = _save_upload(file)
    out = path.with_name(path.stem + "_boxes.jpg")
    visualization.draw_boxes(analyzer.detector, str(path), str(out))
    return FileResponse(out, media_type="image/jpeg")


@app.post("/visualize/masks")
async def visualize_masks(file: UploadFile = File(...)):
    path = _save_upload(file)
    out = path.with_name(path.stem + "_masks.jpg")
    visualization.draw_masks(analyzer.detector, str(path), str(out))
    return FileResponse(out, media_type="image/jpeg")


@app.get("/health")
def health():
    return {"status": "healthy"}
