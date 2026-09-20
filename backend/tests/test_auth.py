def test_login_and_me(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {response.json()['access_token']}"})
    assert me.status_code == 200
    assert me.json()["role"] == "ADMIN"


def test_role_protection(client, admin_headers):
    created = client.post("/api/admin/users", headers=admin_headers, json={"username": "guard1", "password": "guard123", "role": "SECURITY"})
    assert created.status_code == 201
    token = client.post("/api/auth/login", json={"username": "guard1", "password": "guard123"}).json()["access_token"]
    forbidden = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert forbidden.status_code == 403
