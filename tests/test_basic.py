import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    res = client.post("/auth/signup", json={"email": "user@example.com", "password": "secret123"})
    token = res.json()["access_token"]
    return {"token": token}


def test_create_tree_and_person():
    headers = auth_headers()
    tree_res = client.post("/trees", json={"name": "Family"}, headers=headers)
    assert tree_res.status_code == 200
    tree_id = tree_res.json()["id"]

    person_res = client.post(
        f"/trees/{tree_id}/persons",
        json={"first_name": "Ivan", "last_name": "Ivanov", "gender": "male"},
        headers=headers,
    )
    assert person_res.status_code == 200
    data = person_res.json()
    assert data["first_name"] == "Ivan"

    list_res = client.get(f"/trees/{tree_id}/persons", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
