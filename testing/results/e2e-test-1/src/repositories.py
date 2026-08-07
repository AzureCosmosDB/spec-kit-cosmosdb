from azure.cosmos.exceptions import CosmosResourceNotFoundError
from src.database import get_database
from src.models import User, Task
from typing import List, Optional


class UserRepository:
    def __init__(self):
        self.container = get_database().get_container_client("users")

    def create(self, user: User) -> dict:
        return self.container.create_item(body=user.model_dump())

    def get(self, user_id: str) -> Optional[dict]:
        try:
            return self.container.read_item(item=user_id, partition_key=user_id)
        except CosmosResourceNotFoundError:
            return None

    def list_all(self) -> List[dict]:
        return list(self.container.query_items(
            query="SELECT * FROM c WHERE c.type = 'user'",
            enable_cross_partition_query=True,
        ))

    def delete(self, user_id: str):
        self.container.delete_item(item=user_id, partition_key=user_id)


class TaskRepository:
    def __init__(self):
        self.container = get_database().get_container_client("tasks")

    def create(self, task: Task) -> dict:
        return self.container.create_item(body=task.model_dump())

    def get(self, task_id: str, user_id: str) -> Optional[dict]:
        try:
            return self.container.read_item(item=task_id, partition_key=user_id)
        except CosmosResourceNotFoundError:
            return None

    def list_by_user(self, user_id: str) -> List[dict]:
        return list(self.container.query_items(
            query="SELECT * FROM c WHERE c.user_id = @user_id AND c.type = 'task'",
            parameters=[{"name": "@user_id", "value": user_id}],
            partition_key=user_id,
        ))

    def update(self, task_id: str, user_id: str, updates: dict) -> Optional[dict]:
        existing = self.get(task_id, user_id)
        if not existing:
            return None
        for key, value in updates.items():
            if value is not None:
                existing[key] = value
        return self.container.replace_item(item=task_id, body=existing)

    def delete(self, task_id: str, user_id: str):
        self.container.delete_item(item=task_id, partition_key=user_id)
