import os
import httpx
from sqlalchemy import create_engine, text


BASE_URL = "http://127.0.0.1:8000"

DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://api_tester:TON_MOT_DE_PASSE@localhost:5433/taskdb"
)

engine = create_engine(DATABASE_URL)


def test_task_saved_in_database():

    # 1. Créer une tâche via l'API
    response = httpx.post(
        f"{BASE_URL}/tasks",
        json={
            "title": "Database Test",
            "description": "Verify data directly in PostgreSQL"
        }
    )

    assert response.status_code == 201

    task = response.json()
    task_id = task["id"]

    # 2. Vérifier directement dans PostgreSQL
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT id, title, description, completed
                FROM tasks
                WHERE id = :task_id
            """),
            {"task_id": task_id}
        )

        db_task = result.mappings().first()

    # 3. Comparer API ↔ Database
    assert db_task is not None
    assert db_task["id"] == task_id
    assert db_task["title"] == "Database Test"
    assert db_task["description"] == "Verify data directly in PostgreSQL"
    assert db_task["completed"] is False

    # 4. Nettoyage
    httpx.delete(f"{BASE_URL}/tasks/{task_id}")
