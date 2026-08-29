from app.models.user import User


def register_user(
    client,
    first_name: str,
    last_name: str,
    email: str,
    password: str = "test12345",
):
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "organization": "KFU",
            "password": password,
            "password_confirm": password,
        },
    )

    assert response.status_code == 200
    return response.json()


def login_user(client, email: str, password: str = "test12345") -> str:
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_director_create_invite_and_researcher_accept(client, db_session):
    director_data = register_user(
        client,
        first_name="Director",
        last_name="User",
        email="director@example.com",
    )

    researcher_data = register_user(
        client,
        first_name="Researcher",
        last_name="User",
        email="researcher@example.com",
    )

    director = db_session.query(User).filter(User.id == director_data["id"]).first()

    director.role = "director"
    db_session.commit()

    director_token = login_user(client, "director@example.com")
    researcher_token = login_user(client, "researcher@example.com")

    invite_response = client.post(
        "/api/invites",
        json={
            "expires_in_days": 7,
        },
        headers={
            "Authorization": f"Bearer {director_token}",
        },
    )

    assert invite_response.status_code == 200

    invite_data = invite_response.json()
    invite_code = invite_data["code"]

    check_response = client.get(f"/api/invites/{invite_code}")

    assert check_response.status_code == 200
    assert check_response.json()["is_active"] is True

    accept_response = client.post(
        f"/api/invites/{invite_code}/accept",
        headers={
            "Authorization": f"Bearer {researcher_token}",
        },
    )

    assert accept_response.status_code == 200

    accepted_user = accept_response.json()

    assert accepted_user["id"] == researcher_data["id"]
    assert accepted_user["director_id"] == director_data["id"]
