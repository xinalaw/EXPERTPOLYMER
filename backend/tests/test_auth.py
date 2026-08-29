def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test_user@example.com",
            "organization": "KFU",
            "password": "test12345",
            "password_confirm": "test12345",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["username"] == "Test User"
    assert data["email"] == "test_user@example.com"
    assert data["role"] == "researcher"


def test_login_user(client):
    client.post(
        "/api/auth/register",
        json={
            "first_name": "Login",
            "last_name": "User",
            "email": "login_user@example.com",
            "organization": "KFU",
            "password": "test12345",
            "password_confirm": "test12345",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "login_user@example.com",
            "password": "test12345",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client):
    client.post(
        "/api/auth/register",
        json={
            "first_name": "Me",
            "last_name": "User",
            "email": "me_user@example.com",
            "organization": "KFU",
            "password": "test12345",
            "password_confirm": "test12345",
        },
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "me_user@example.com",
            "password": "test12345",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "Me"
    assert data["last_name"] == "User"
    assert data["username"] == "Me User"
    assert data["email"] == "me_user@example.com"
    assert data["role"] == "researcher"
