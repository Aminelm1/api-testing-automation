from fastapi.responses import FileResponse
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.database import engine

app = FastAPI()

@app.get("/")
def web_interface():
    return FileResponse("app/static/index.html")


class Task(BaseModel):
    title: str
    description: str

class TaskUpdate(BaseModel):
    completed: bool

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: Task):

    query = text("""
        INSERT INTO tasks (title, description)
        VALUES (:title, :description)
        RETURNING id, title, description, completed
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "title": task.title,
                "description": task.description
            }
        )

        created_task = result.mappings().one()

    return dict(created_task)
@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    query = text("""
        SELECT id, title, description, completed
        FROM tasks
        WHERE id = :task_id
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"task_id": task_id}
        )

        task = result.mappings().first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return dict(task)

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):

    query = text("""
        UPDATE tasks
        SET completed = :completed
        WHERE id = :task_id
        RETURNING id, title, description, completed
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "completed": task.completed,
                "task_id": task_id
            }
        )

        updated_task = result.mappings().first()

    if updated_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return dict(updated_task)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):

    query = text("""
        DELETE FROM tasks
        WHERE id = :task_id
        RETURNING id
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {"task_id": task_id}
        )

        deleted_task = result.first()

    if deleted_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return None
