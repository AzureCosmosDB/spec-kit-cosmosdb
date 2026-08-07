from fastapi import FastAPI, HTTPException
from azure.cosmos.exceptions import CosmosHttpResponseError
from src.config import settings
from src.database import init_database, client
from src.models import (
    User, Task, CreateUserRequest, CreateTaskRequest, UpdateTaskRequest
)
from src.repositories import UserRepository, TaskRepository

app = FastAPI(title="Todo API", version="1.0.0")


@app.on_event("startup")
def startup():
    init_database()


@app.get("/health")
def health():
    try:
        client.get_database_account()
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# --- Users ---

@app.post("/users", status_code=201)
def create_user(req: CreateUserRequest):
    repo = UserRepository()
    user = User(username=req.username, email=req.email)
    user.user_id = user.id  # partition key = id for users
    try:
        result = repo.create(user)
        return result
    except CosmosHttpResponseError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/users/{user_id}")
def get_user(user_id: str):
    repo = UserRepository()
    user = repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users")
def list_users():
    repo = UserRepository()
    return repo.list_all()


# --- Tasks ---

@app.post("/users/{user_id}/tasks", status_code=201)
def create_task(user_id: str, req: CreateTaskRequest):
    repo = TaskRepository()
    task = Task(user_id=user_id, title=req.title, description=req.description)
    try:
        result = repo.create(task)
        return result
    except CosmosHttpResponseError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/users/{user_id}/tasks")
def list_tasks(user_id: str):
    repo = TaskRepository()
    return repo.list_by_user(user_id)


@app.get("/users/{user_id}/tasks/{task_id}")
def get_task(user_id: str, task_id: str):
    repo = TaskRepository()
    task = repo.get(task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/users/{user_id}/tasks/{task_id}")
def update_task(user_id: str, task_id: str, req: UpdateTaskRequest):
    repo = TaskRepository()
    updates = req.model_dump(exclude_unset=True)
    result = repo.update(task_id, user_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@app.delete("/users/{user_id}/tasks/{task_id}", status_code=204)
def delete_task(user_id: str, task_id: str):
    repo = TaskRepository()
    try:
        repo.delete(task_id, user_id)
    except CosmosHttpResponseError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=e.status_code, detail=str(e))
