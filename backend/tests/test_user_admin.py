from app.commands.create_admin import BootstrapAdminError, create_first_admin
from app.models.action_log import ActionLog
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
