import os
import uuid
from datetime import date, datetime, time, timedelta, timezone

from fastapi import status, HTTPException, UploadFile
from kombu.exceptions import OperationalError
from sqlalchemy.orm import Session

from app.models.analysis_result import AnalysisResult
from app.models.analysis_task import AnalysisTask
from app.models.user import User
from app.services.log_service import create_action_log
from app.services.access_service import (
    can_access_analysis_result,
)
from app.services.ml_service import analysis_material_image
from app.tasks.analysis_tasks import analyze_image_task


UPLOAD_DIR = "app/static/uploads"
PROCESSED_DIR = "app/static/processed"


def remove_static_file(static_path: str | None):
    if not static_path:
        return

    relative_path = static_path.lstrip("/")
    file_path = os.path.join("app", *relative_path.split("/"))

    if os.path.exists(file_path):
        os.remove(file_path)


def get_analysis_result(result_id: int, db: Session, current_user: User):
    analysis_result = (
        db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    )

    if not analysis_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результат анализа не найден",
        )

    if not can_access_analysis_result(db, current_user, analysis_result):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому результату",
        )

    return analysis_result


def delete_analysis_result(
    result_id: int,
    db: Session,
    current_user: User,
):
    analysis_result = (
        db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    )

    if not analysis_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результат анализа не найден",
        )

    if not can_access_analysis_result(db, current_user, analysis_result):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к удалению этого результата",
        )

    deleted_result_info = {
        "result_id": analysis_result.id,
        "image_path": analysis_result.image_path,
        "processed_image_path": analysis_result.processed_image_path,
        "user_id": analysis_result.user_id,
    }

    # Keep the task audit trail after its result is deleted. PostgreSQL refuses
    # to delete a result while a task still references it.
    db.query(AnalysisTask).filter(AnalysisTask.result_id == result_id).update(
        {AnalysisTask.result_id: None}, synchronize_session="fetch"
    )

    db.delete(analysis_result)
    db.commit()

    remove_static_file(deleted_result_info["image_path"])
    remove_static_file(deleted_result_info["processed_image_path"])

    create_action_log(
        db=db,
        actor_id=current_user.id,
        action="DELETE_ANALYSIS_RESULT",
        target_type="analysis_result",
        target_id=result_id,
        details=deleted_result_info,
    )

    return {"message": "Результат анализа удален"}


def get_analysis_history(
    db: Session,
    current_user: User,
    user_id: int | None = None,
    analysis_date: date | None = None,
    limit: int = 20,
    offset: int = 0,
):
    query = db.query(AnalysisResult)

    if current_user.role == "admin":
        if user_id is not None:
            query = query.filter(AnalysisResult.user_id == user_id)

    elif current_user.role == "director":
        researcher_ids_query = db.query(User.id).filter(
            User.director_id == current_user.id
        )

        query = query.filter(AnalysisResult.user_id.in_(researcher_ids_query))

        if user_id is not None:
            researcher = db.query(User).filter(User.id == user_id).first()

            if not researcher or researcher.director_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к истории этого пользователя",
                )

            query = query.filter(AnalysisResult.user_id == user_id)

    elif current_user.role == "researcher":
        query = query.filter(AnalysisResult.user_id == current_user.id)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    if analysis_date is not None:
        day_start = datetime.combine(analysis_date, time.min, tzinfo=timezone.utc)
        query = query.filter(
            AnalysisResult.created_at >= day_start,
            AnalysisResult.created_at < day_start + timedelta(days=1),
        )

    return (
        query.order_by(AnalysisResult.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def analyze_image(file: UploadFile, db: Session, current_user: User):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно загружать только изображения",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    file_extension = os.path.splitext(file.filename or "")[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    original_file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(original_file_path, "wb") as buffer:
        buffer.write(file.file.read())

    processed_filename = f"processed_{unique_filename}"
    processed_file_path = os.path.join(PROCESSED_DIR, processed_filename)

    try:
        analysis_data = analysis_material_image(
            original_file_path=original_file_path,
            processed_file_path=processed_file_path,
        )
    except ValueError:
        remove_static_file(f"/static/uploads/{unique_filename}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось обработать изображение",
        )

    db_image_path = f"/static/uploads/{unique_filename}"
    db_processed_image_path = f"/static/processed/{processed_filename}"

    analysis_result = AnalysisResult(
        image_path=db_image_path,
        processed_image_path=db_processed_image_path,
        original_filename=file.filename or unique_filename,
        result=analysis_data["result"],
        result_data=analysis_data["result_data"],
        confidence=analysis_data["confidence"],
        width=analysis_data["width"],
        height=analysis_data["height"],
        user_id=current_user.id,
    )

    db.add(analysis_result)
    db.commit()
    db.refresh(analysis_result)

    return analysis_result


def analyze_image_async(
    file: UploadFile,
    db: Session,
    current_user: User,
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно загружать только изображения",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    file_extension = os.path.splitext(file.filename or "")[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    original_file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(original_file_path, "wb") as buffer:
        buffer.write(file.file.read())

    task_id = str(uuid.uuid4())
    analysis_task = AnalysisTask(
        task_id=task_id,
        status="PENDING",
        image_path=f"/static/uploads/{unique_filename}",
        original_filename=file.filename or unique_filename,
        user_id=current_user.id,
    )

    db.add(analysis_task)
    db.commit()
    db.refresh(analysis_task)

    # A fast worker must be able to find the job before receiving the message.
    try:
        analyze_image_task.apply_async(
            task_id=task_id,
            kwargs={
                "image_path": original_file_path,
                "original_filename": file.filename or unique_filename,
                "user_id": current_user.id,
            },
        )
    except OperationalError:
        analysis_task.status = "FAILURE"
        analysis_task.error_message = "Не удалось отправить задачу в очередь анализа"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=analysis_task.error_message,
        )

    return {
        "task_id": task_id,
        "status": analysis_task.status,
    }


def get_analysis_task_status(
    task_id: str,
    db: Session,
    current_user: User,
):
    analysis_task = (
        db.query(AnalysisTask).filter(AnalysisTask.task_id == task_id).first()
    )

    if not analysis_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача анализа не найдена",
        )

    if current_user.role != "admin" and analysis_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой задаче",
        )

    return {
        "task_id": analysis_task.task_id,
        "status": analysis_task.status,
        "result_id": analysis_task.result_id,
        "error_message": analysis_task.error_message,
        "created_at": analysis_task.created_at,
        "updated_at": analysis_task.updated_at,
    }
