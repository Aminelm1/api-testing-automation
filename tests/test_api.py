import httpx

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    response = httpx.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_task_crud():
    # 1. CREATE
    response = httpx.post(
        f"{BASE_URL}/tasks",
        json={
            "title": "Pytest Task",
            "description": "Automated API testing"
        }
    )

    assert response.status_code == 201

    created_task = response.json()
    task_id = created_task["id"]

    assert created_task["title"] == "Pytest Task"
    assert created_task["completed"] is False

    # 2. READ
    response = httpx.get(f"{BASE_URL}/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id

    # 3. UPDATE
    response = httpx.patch(
        f"{BASE_URL}/tasks/{task_id}",
        json={"completed": True}
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True

    # 4. DELETE
    response = httpx.delete(
        f"{BASE_URL}/tasks/{task_id}"
    )

    assert response.status_code == 204

    # 5. Vérifier que la tâche n'existe plus
    response = httpx.get(f"{BASE_URL}/tasks/{task_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_get_unknown_task():
    response = httpx.get(f"{BASE_URL}/tasks/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_create_task_missing_title():
    response = httpx.post(
        f"{BASE_URL}/tasks",
        json={
            "description": "Task without title"
        }
    )

    assert response.status_code == 422


def test_create_task_invalid_title():
    response = httpx.post(
        f"{BASE_URL}/tasks",
        json={
            "title": {"invalid": "value"},
            "description": "Invalid title type"
        }
    )

    assert response.status_code == 422
