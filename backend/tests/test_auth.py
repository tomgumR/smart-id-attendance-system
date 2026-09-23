def test_login_and_me(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123", "role": "ADMIN"})
    assert response.status_code == 200
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {response.json()['access_token']}"})
    assert me.status_code == 200
    assert me.json()["role"] == "ADMIN"


def test_role_protection(client, admin_headers):
    created = client.post("/api/admin/users", headers=admin_headers, json={"username": "guard1", "password": "guard123", "role": "SECURITY"})
    assert created.status_code == 201
    token = client.post("/api/auth/login", json={"username": "guard1", "password": "guard123", "role": "SECURITY"}).json()["access_token"]
    forbidden = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert forbidden.status_code == 403


def test_login_rejects_account_for_wrong_selected_role(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123", "role": "PROFESSOR"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "This account is not authorized for the selected role"


def test_loopback_frontend_origin_is_allowed(client):
    response = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_admin_can_create_list_and_delete_professor(client, admin_headers):
    created = client.post(
        "/api/admin/users",
        headers=admin_headers,
        json={"username": "professor2", "password": "professor234", "role": "PROFESSOR"},
    )
    assert created.status_code == 201
    professor_id = created.json()["id"]

    professors = client.get("/api/admin/professors", headers=admin_headers)
    assert professors.status_code == 200
    assert [user["username"] for user in professors.json()] == ["professor2"]

    deleted = client.delete(f"/api/admin/professors/{professor_id}", headers=admin_headers)
    assert deleted.status_code == 204
    assert client.get("/api/admin/professors", headers=admin_headers).json() == []

    login = client.post(
        "/api/auth/login",
        json={"username": "professor2", "password": "professor234", "role": "PROFESSOR"},
    )
    assert login.status_code == 401
