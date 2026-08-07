"""Workflow/Task Management API - Azure Cosmos DB"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import get_settings
from repository import TaskRepository, ProjectRepository, AssigneeTaskRepository
from service import TaskService, ProjectService
from azure.cosmos.aio import CosmosClient

settings = get_settings()
cosmos_client = None
task_service = None
project_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global cosmos_client, task_service, project_service
    cosmos_client = CosmosClient(settings.cosmos_endpoint, settings.cosmos_key)
    database = cosmos_client.get_database_client(settings.cosmos_database)
    
    task_repo = TaskRepository(database.get_container_client("tasks"))
    project_repo = ProjectRepository(database.get_container_client("projects"))
    assignee_task_repo = AssigneeTaskRepository(database.get_container_client("assigneeTasks"))
    
    task_service = TaskService(task_repo)
    project_service = ProjectService(project_repo)
    
    yield
    
    await cosmos_client.close()


app = FastAPI(title="Workflow Manager", lifespan=lifespan)


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/projects/{project_id}/tasks")
async def get_project_tasks(project_id: str, status: str = None, priority: str = None, page: int = 1):
    tasks = await task_service.get_tasks_by_project(project_id, status, priority, page)
    return tasks


@app.get("/api/projects/{project_id}/tasks/{task_id}")
async def get_task(project_id: str, task_id: str):
    task = await task_service.get_task(project_id, task_id)
    return task


@app.patch("/api/projects/{project_id}/tasks/{task_id}")
async def update_task(project_id: str, task_id: str, update: dict):
    result = await task_service.update_task(project_id, task_id, update)
    return result


@app.post("/api/projects/{project_id}/tasks/{task_id}/transition")
async def transition_task(project_id: str, task_id: str, body: dict):
    result = await task_service.transition_status(project_id, task_id, body["status"], body.get("changedBy", "system"))
    return result


@app.get("/api/projects/{project_id}/tasks/{task_id}/comments")
async def get_comments(project_id: str, task_id: str):
    comments = await task_service.get_comments(project_id, task_id)
    return comments


@app.post("/api/projects/{project_id}/tasks/{task_id}/comments", status_code=201)
async def create_comment(project_id: str, task_id: str, comment: dict):
    result = await task_service.create_comment(project_id, task_id, comment)
    return result


@app.get("/api/projects/{project_id}/tasks/{task_id}/history")
async def get_history(project_id: str, task_id: str):
    history = await task_service.get_status_history(project_id, task_id)
    return history


@app.get("/api/assignees/{assignee_id}/tasks")
async def get_assignee_tasks(assignee_id: str):
    tasks = await task_service.get_tasks_by_assignee(assignee_id)
    return tasks


@app.get("/api/projects/{project_id}/activity")
async def get_activity(project_id: str, from_date: str = None, to_date: str = None):
    activity = await task_service.get_activity_log(project_id, from_date, to_date)
    return activity


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
