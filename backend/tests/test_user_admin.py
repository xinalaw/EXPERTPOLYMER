from datetime import datetime, timezone

from app.commands.create_admin import BootstrapAdminError, create_first_admin
from app.models.action_log import ActionLog
from app.models.analysis_task import AnalysisTask
from app.models.director_invite import DirectorInvite
from app.models.user import User
from app.utils.security import create_access_token, hash_password


def _auth(user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def _user(db_session, email: str, role: str = "researcher") -> User:
    user = User(
        username=email.split("@")[0],
        email=email,
        password_hash=hash_password("test12345"),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_admin_can_promote_user_and_action_is_logged(client, db_session):
    admin = _user(db_session, "admin@example.com", "admin")
    researcher = _user(db_session, "researcher@example.com")

    response = client.patch(
        f"/api/users/{researcher.id}/role",
        json={"role": "admin"},
        headers=_auth(admin),
    )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    log = db_session.query(ActionLog).filter_by(action="CHANGE_USER_ROLE").one()
    assert log.actor_id == admin.id
    assert log.target_id == researcher.id
    assert log.details == {"old_role": "researcher", "new_role": "admin"}


def test_admin_cannot_demote_self(client, db_session):
    admin = _user(db_session, "admin@example.com", "admin")

    response = client.patch(
        f"/api/users/{admin.id}/role",
        json={"role": "researcher"},
        headers=_auth(admin),
    )

    assert response.status_code == 400
    assert db_session.get(User, admin.id).role == "admin"


def test_create_first_admin_is_one_time(db_session):
    admin = create_first_admin(
        db_session,
        email="first-admin@example.com",
        password="safe-password",
        first_name="First",
        last_name="Admin",
    )
    assert admin.role == "admin"

    try:
        create_first_admin(
            db_session,
            email="second-admin@example.com",
            password="safe-password",
            first_name="Second",
            last_name="Admin",
        )
    except BootstrapAdminError as error:
        assert "уже существует" in str(error)
    else:
        raise AssertionError("A second bootstrap administrator was created")


def test_admin_dashboard_and_lists_require_admin(client, db_session):
    admin = _user(db_session, "admin@example.com", "admin")
    researcher = _user(db_session, "researcher@example.com")
    task = AnalysisTask(
        task_id="task-1",
        status="PENDING",
        image_path="/static/uploads/test.png",
        original_filename="test.png",
        user_id=researcher.id,
    )
    invite = DirectorInvite(
        code="invite-1",
        director_id=admin.id,
        is_active=True,
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add_all([task, invite])
    db_session.commit()

    forbidden = client.get("/api/admin/dashboard", headers=_auth(researcher))
    assert forbidden.status_code == 403

    dashboard = client.get("/api/admin/dashboard", headers=_auth(admin))
    assert dashboard.status_code == 200
    assert dashboard.json()["users_total"] == 2
    assert dashboard.json()["tasks_pending"] == 1
    assert dashboard.json()["active_invites"] == 1

    tasks = client.get("/api/admin/tasks", headers=_auth(admin))
    assert tasks.status_code == 200
    assert tasks.json()[0]["task_id"] == "task-1"

    invites = client.get("/api/admin/invites", headers=_auth(admin))
    assert invites.status_code == 200
    assert invites.json()[0]["code"] == "invite-1"
