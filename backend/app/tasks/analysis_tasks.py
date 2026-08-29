import os

import cv2
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.analysis_result import AnalysisResult
from app.models.analysis_task import AnalysisTask
from app.services.ml_service import analysis_material_image
from app.tasks.celery_app import celery_app


PROCESSED_DIR = "app/static/processed"


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def analyze_image_task(
    self,
    image_path: str,
    original_filename: str,
    user_id: int,
):
    db: Session = SessionLocal()

    try:
        analysis_task = (
            db.query(AnalysisTask)
            .filter(AnalysisTask.task_id == self.request.id)
            .first()
        )

        if analysis_task:
            analysis_task.status = "PROCESSING"
            db.commit()

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Не удалось обработать изображение")

        processed_filename = f"processed_{os.path.basename(image_path)}"

        processed_file_path = os.path.join(
            PROCESSED_DIR,
            processed_filename,
        )

        analysis_data = analysis_material_image(
            original_file_path=image_path,
            processed_file_path=processed_file_path,
        )

        analysis_result = AnalysisResult(
            image_path=f"/static/uploads/{os.path.basename(image_path)}",
            processed_image_path=f"/static/processed/{processed_filename}",
            original_filename=original_filename,
            result=analysis_data["result"],
            result_data=analysis_data["result_data"],
            confidence=analysis_data["confidence"],
            width=analysis_data["width"],
            height=analysis_data["height"],
            user_id=user_id,
        )

        db.add(analysis_result)
        db.commit()
        db.refresh(analysis_result)

        if analysis_task:
            analysis_task.status = "SUCCESS"
            analysis_task.result_id = analysis_result.id
            db.commit()

        return {
            "status": "SUCCESS",
            "result_id": analysis_result.id,
        }

    except Exception as e:
        analysis_task = (
            db.query(AnalysisTask)
            .filter(AnalysisTask.task_id == self.request.id)
            .first()
        )

        if self.request.retries < self.max_retries:
            if analysis_task:
                analysis_task.status = "RETRY"
                analysis_task.error_message = str(e)
                db.commit()

            raise self.retry(exc=e)

        if analysis_task:
            analysis_task.status = "FAILURE"
            analysis_task.error_message = str(e)
            db.commit()

        return {
            "status": "FAILURE",
            "error": str(e),
        }

    finally:
        db.close()
