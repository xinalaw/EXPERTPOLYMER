from fastapi import Depends, APIRouter, File, UploadFile, Query
from sqlalchemy.orm import Session
from datetime import date

from app.controllers.analysis_controller import (
    analyze_image,
    analyze_image_async,
    get_analysis_task_status,
    get_analysis_result,
    get_analysis_history,
    delete_analysis_result,
)
from app.database.dependencies import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.analysis import AnalysisResultResponseSchema

router = APIRouter(
    prefix="/api",
    tags=["Image Analysis"],
)


@router.post(
    "/analyze",
    response_model=AnalysisResultResponseSchema,
    summary="Загрузка изображения на анализ",
    description="""
    Загружает изображение, выполняется OpenCV preprocessing,
    создает processed изображение и сохранает результат анализа.
    """,
)
def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analyze_image(file, db, current_user)


@router.post(
    "/analyze/async",
    summary="Асинхронная загрузка изображения на анализ",
    description="Сохраняет изображение и запускает фоновую задачу анализа через Celery.",
)
def analyze_image_async_route(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analyze_image_async(
        file=file,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/analyze/tasks/{task_id}",
    summary="Получение статуса фоновой задачи анализа",
    description="Возвращает статус задачи анализа из базы данных.",
)
def get_analysis_task_status_route(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_analysis_task_status(
        task_id=task_id,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/results/{result_id}",
    response_model=AnalysisResultResponseSchema,
    summary="Получение результата анализа по id",
)
def get_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_analysis_result(result_id, db, current_user)


@router.delete(
    "/results/{result_id}",
    summary="Удаление результата анализа",
)
def delete_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_analysis_result(result_id, db, current_user)


@router.get(
    "/history",
    response_model=list[AnalysisResultResponseSchema],
    summary="Получение истории анализов",
    description="""
    Возвращает историю анализов в зависимости от роли пользователя:
    -admin: все анализы
    -director: анализы researcher прикрепленных к нему
    -researcher: только свои анализы
    """,
)
def get_history(
    user_id: int | None = Query(default=None),
    analysis_date: date | None = Query(default=None, alias="date"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_analysis_history(
        db=db,
        current_user=current_user,
        user_id=user_id,
        analysis_date=analysis_date,
        limit=limit,
        offset=offset,
    )
