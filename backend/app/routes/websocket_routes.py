import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.analysis_task import AnalysisTask

router = APIRouter(
    prefix="/api/ws",
    tags=["WebSocket"],
)


@router.websocket("/analyze/tasks/{task_id}")
async def analysis_task_status_websocket(
    websocket: WebSocket,
    task_id: str,
):
    await websocket.accept()

    try:
        while True:
            db: Session = SessionLocal()

            try:
                analysis_task = (
                    db.query(AnalysisTask)
                    .filter(AnalysisTask.task_id == task_id)
                    .first()
                )

                if not analysis_task:
                    await websocket.send_json(
                        {
                            "task_id": task_id,
                            "status": "NOT_FOUND",
                            "result_id": None,
                            "error_message": "Задача анализа не найдена",
                        }
                    )
                    break

                await websocket.send_json(
                    {
                        "task_id": analysis_task.task_id,
                        "status": analysis_task.status,
                        "result_id": analysis_task.result_id,
                        "error_message": analysis_task.error_message,
                    }
                )

                if analysis_task.status in ["SUCCESS", "FAILED"]:
                    break

            finally:
                db.close()

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass

    finally:
        await websocket.close()
