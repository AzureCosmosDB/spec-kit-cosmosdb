"""Business logic for workflow management."""
import uuid
from datetime import datetime


VALID_TRANSITIONS = {
    "backlog": ["todo"],
    "todo": ["in_progress"],
    "in_progress": ["in_review", "blocked"],
    "blocked": ["in_progress"],
    "in_review": ["done", "in_progress"],
    "done": [],
}


def validate_transition(current: str, target: str) -> bool:
    return target in VALID_TRANSITIONS.get(current, [])


class TaskService:
    def __init__(self, task_repo):
        self.task_repo = task_repo

    async def get_tasks_by_project(self, project_id: str, status: str = None, priority: str = None, page: int = 1):
        return await self.task_repo.get_tasks_by_project(project_id, status, priority, page)

    async def get_task(self, project_id: str, task_id: str):
        return await self.task_repo.get_task(project_id, task_id)

    async def update_task(self, project_id: str, task_id: str, update: dict):
        task = await self.task_repo.get_task(project_id, task_id)
        task.update(update)
        task["updatedAt"] = datetime.utcnow().isoformat()
        return await self.task_repo.replace_task(task_id, task, project_id)

    async def transition_status(self, project_id: str, task_id: str, target_status: str, changed_by: str):
        task = await self.task_repo.get_task(project_id, task_id)
        current_status = task["status"]
        
        if not validate_transition(current_status, target_status):
            raise Exception(f"409: Invalid transition from {current_status} to {target_status}")
        
        # Update task status
        task["status"] = target_status
        task["updatedAt"] = datetime.utcnow().isoformat()
        await self.task_repo.replace_task(task_id, task, project_id)
        
        # Create audit record
        history = {
            "id": str(uuid.uuid4()),
            "projectId": project_id,
            "type": "statusHistory",
            "taskId": task_id,
            "fromStatus": current_status,
            "toStatus": target_status,
            "changedBy": changed_by,
            "changedAt": datetime.utcnow().isoformat(),
        }
        await self.task_repo.create_item(history)
        
        return task

    async def get_comments(self, project_id: str, task_id: str):
        return await self.task_repo.get_comments(project_id, task_id)

    async def create_comment(self, project_id: str, task_id: str, comment: dict):
        item = {
            "id": str(uuid.uuid4()),
            "projectId": project_id,
            "type": "comment",
            "taskId": task_id,
            "authorId": comment["authorId"],
            "body": comment["body"],
            "createdAt": datetime.utcnow().isoformat(),
        }
        return await self.task_repo.create_item(item)

    async def get_status_history(self, project_id: str, task_id: str):
        return await self.task_repo.get_status_history(project_id, task_id)

    async def get_tasks_by_assignee(self, assignee_id: str):
        # Uses denormalized assigneeTasks container
        pass  # Would use AssigneeTaskRepository

    async def get_activity_log(self, project_id: str, from_date: str = None, to_date: str = None):
        return await self.task_repo.get_activity_log(project_id, from_date, to_date)


class ProjectService:
    def __init__(self, project_repo):
        self.project_repo = project_repo

    async def get_project(self, project_id: str):
        return await self.project_repo.get_project(project_id)
