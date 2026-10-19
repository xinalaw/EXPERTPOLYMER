from datetime import datetime, timezone
from io import BytesIO

import cv2
import numpy as np
import pytest
from kombu.exceptions import OperationalError

from app.controllers import analysis_controller
from app.models.action_log import ActionLog
from app.models.analysis_result import AnalysisResult
from app.models.analysis_task import AnalysisTask
from app.models.user import User
from app.utils.security import create_access_token


def make_user(db_session, email, role="researcher", director_id=None):
    user = User(
        username=email.split("@")[0],
        email=email,
        password_hash="unused-in-token-tests",
        role=role,
        director_id=director_id,
    )
    db_session.add(user)
    db_session.commit()
    return user


def auth(user):
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user.id)})}"}


def make_result(db_session, user, filename, created_at):
    result = AnalysisResult(
        user_id=user.id,
        image_path=f"/static/uploads/{filename}",
        original_filename=filename,
        result="Ready",
        confidence=0.95,
        created_at=created_at,
    )
    db_session.add(result)
    db_session.commit()
    return result


def image_upload():
    success, encoded = cv2.imencode(".png", np.zeros((10, 10, 3), dtype=np.uint8))
    assert success
    return {"file": ("sample.png", BytesIO(encoded.tobytes()), "image/png")}


@pytest.mark.parametrize("subject", ["not-an-id", "0", "-1", "9999999999999999999999999"])
def test_invalid_token_subject_returns_401(client, subject):
    token = create_access_token({"sub": subject})
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_history_date_and_pagination_preserve_role_scope(client, db_session):
    director = make_user(db_session, "director@example.com", "director")
    researcher = make_user(db_session, "researcher@example.com", director_id=director.id)
    stranger = make_user(db_session, "stranger@example.com")
    make_result(db_session, researcher, "previous.png", datetime(2026, 10, 18, 23, 59, tzinfo=timezone.utc))
    first = make_result(db_session, researcher, "first.png", datetime(2026, 10, 19, 0, 0, tzinfo=timezone.utc))
    second = make_result(db_session, researcher, "second.png", datetime(2026, 10, 19, 23, 59, tzinfo=timezone.utc))
    make_result(db_session, researcher, "next.png", datetime(2026, 10, 20, 0, 0, tzinfo=timezone.utc))
    make_result(db_session, stranger, "private.png", datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc))

    response = client.get("/api/history?date=2026-10-19&limit=1", headers=auth(director))
    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [second.id]
    response = client.get("/api/history?date=2026-10-19&limit=1&offset=1", headers=auth(director))
    assert [row["id"] for row in response.json()] == [first.id]
    response = client.get(f"/api/history?user_id={stranger.id}", headers=auth(director))
    assert response.status_code == 403


def test_logs_date_filter_and_access(client, db_session):
    admin = make_user(db_session, "admin@example.com", "admin")
    researcher = make_user(db_session, "researcher@example.com")
    for day in (18, 19, 20):
        db_session.add(ActionLog(
            actor_id=admin.id,
            action="CHANGE_USER_ROLE",
            target_type="user",
            created_at=datetime(2026, 10, day, tzinfo=timezone.utc),
        ))
    db_session.commit()

    response = client.get("/api/logs?date=2026-10-19", headers=auth(admin))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["created_at"].startswith("2026-10-19")
    assert client.get("/api/logs", headers=auth(researcher)).status_code == 403


def test_admin_assignment_is_visible_only_to_assigned_director(client, db_session):
    admin = make_user(db_session, "admin@example.com", "admin")
    director = make_user(db_session, "director@example.com", "director")
    other_director = make_user(db_session, "other-director@example.com", "director")
    researcher = make_user(db_session, "researcher@example.com")
    make_user(db_session, "other-researcher@example.com", director_id=other_director.id)

    assigned = client.patch(
        f"/api/users/{researcher.id}/director",
        json={"director_id": director.id},
        headers=auth(admin),
    )
    assert assigned.status_code == 200
    assert assigned.json()["director_id"] == director.id
    team = client.get("/api/director/researchers", headers=auth(director))
    assert team.status_code == 200
    assert [row["id"] for row in team.json()] == [researcher.id]
    search = client.get("/api/users/search?query=researcher", headers=auth(director))
    assert search.status_code == 200
    assert [row["id"] for row in search.json()] == [researcher.id]

    # Role claims from an older token never override the user's current DB role.
    stale_token = create_access_token({"sub": str(researcher.id), "role": "admin"})
    forbidden = client.get("/api/users", headers={"Authorization": f"Bearer {stale_token}"})
    assert forbidden.status_code == 403
    assert client.get("/api/director/researchers", headers=auth(researcher)).status_code == 403
    log = db_session.query(ActionLog).filter_by(action="ASSIGN_DIRECTOR").one()
    assert log.actor_id == admin.id
    assert log.target_id == researcher.id


def test_delete_async_result_keeps_task_history(client, db_session):
    researcher = make_user(db_session, "researcher@example.com")
    result = make_result(db_session, researcher, "already-missing.png", datetime.now(timezone.utc))
    task = AnalysisTask(
        task_id="completed-task",
        status="SUCCESS",
        user_id=researcher.id,
        image_path=result.image_path,
        original_filename=result.original_filename,
        result_id=result.id,
    )
    db_session.add(task)
    db_session.commit()

    response = client.delete(f"/api/results/{result.id}", headers=auth(researcher))
    assert response.status_code == 200
    db_session.refresh(task)
    assert task.result_id is None
    assert task.status == "SUCCESS"
    assert db_session.get(AnalysisResult, result.id) is None


def test_async_job_is_saved_before_worker_can_receive_it(client, db_session, monkeypatch):
    researcher = make_user(db_session, "researcher@example.com")

    def publish(args=None, kwargs=None, task_id=None, **options):
        # A worker uses another session: it must see an already committed job.
        with type(db_session)(bind=db_session.get_bind()) as worker_db:
            job = worker_db.query(AnalysisTask).filter_by(task_id=task_id).one()
            assert job.user_id == researcher.id
            assert kwargs["user_id"] == researcher.id

    monkeypatch.setattr(analysis_controller.analyze_image_task, "apply_async", publish)
    response = client.post("/api/analyze/async", headers=auth(researcher), files=image_upload())
    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"


def test_broker_failure_is_visible_in_admin_tasks(client, db_session, monkeypatch):
    researcher = make_user(db_session, "researcher@example.com")

    def publish(*args, **kwargs):
        raise OperationalError("Redis unavailable")

    monkeypatch.setattr(analysis_controller.analyze_image_task, "apply_async", publish)
    response = client.post("/api/analyze/async", headers=auth(researcher), files=image_upload())
    assert response.status_code == 503
    task = db_session.query(AnalysisTask).one()
    assert task.status == "FAILURE"
    assert task.error_message
