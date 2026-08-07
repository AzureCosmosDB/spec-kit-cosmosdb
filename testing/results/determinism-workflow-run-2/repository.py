"""Cosmos DB repositories for the workflow system."""


class TaskRepository:
    """Repository for tasks container.
    
    # PARTITION KEY: /projectId
    # JUSTIFICATION: Tasks, comments, and status history are always queried within project context.
    # Tasks-by-assignee served via denormalized assigneeTasks container.
    """

    def __init__(self, container):
        self.container = container

    async def get_tasks_by_project(self, project_id: str, status: str = None, priority: str = None, page: int = 1, page_size: int = 20):
        conditions = ["c.projectId = @projectId", "c.type = 'task'"]
        params = [{"name": "@projectId", "value": project_id}]
        
        if status:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status})
        if priority:
            conditions.append("c.priority = @priority")
            params.append({"name": "@priority", "value": priority})
        
        query = f"SELECT * FROM c WHERE {' AND '.join(conditions)} OFFSET {(page-1)*page_size} LIMIT {page_size}"
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=project_id
        ):
            items.append(item)
        return items

    async def get_task(self, project_id: str, task_id: str):
        return await self.container.read_item(item=task_id, partition_key=project_id)

    async def replace_task(self, task_id: str, body: dict, project_id: str):
        return await self.container.replace_item(item=task_id, body=body)

    async def get_comments(self, project_id: str, task_id: str):
        query = "SELECT * FROM c WHERE c.projectId = @projectId AND c.taskId = @taskId AND c.type = 'comment' ORDER BY c.createdAt ASC"
        params = [
            {"name": "@projectId", "value": project_id},
            {"name": "@taskId", "value": task_id},
        ]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=project_id
        ):
            items.append(item)
        return items

    async def get_status_history(self, project_id: str, task_id: str):
        query = "SELECT * FROM c WHERE c.projectId = @projectId AND c.taskId = @taskId AND c.type = 'statusHistory' ORDER BY c.changedAt ASC"
        params = [
            {"name": "@projectId", "value": project_id},
            {"name": "@taskId", "value": task_id},
        ]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=project_id
        ):
            items.append(item)
        return items

    async def create_item(self, item: dict):
        return await self.container.create_item(body=item)

    async def get_activity_log(self, project_id: str, from_date: str = None, to_date: str = None):
        conditions = ["c.projectId = @projectId", "c.type = 'statusHistory'"]
        params = [{"name": "@projectId", "value": project_id}]
        if from_date:
            conditions.append("c.changedAt >= @from")
            params.append({"name": "@from", "value": from_date})
        if to_date:
            conditions.append("c.changedAt <= @to")
            params.append({"name": "@to", "value": to_date})
        query = f"SELECT * FROM c WHERE {' AND '.join(conditions)} ORDER BY c.changedAt DESC"
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=project_id
        ):
            items.append(item)
        return items


class ProjectRepository:
    """Repository for projects container.
    
    # PARTITION KEY: /id
    # JUSTIFICATION: Projects accessed by own ID.
    """

    def __init__(self, container):
        self.container = container

    async def get_project(self, project_id: str):
        return await self.container.read_item(item=project_id, partition_key=project_id)


class AssigneeTaskRepository:
    """Repository for assigneeTasks container (denormalized view).
    
    # PARTITION KEY: /assigneeId
    # JUSTIFICATION: Denormalized view for "tasks assigned to user" (change-feed populated).
    """

    def __init__(self, container):
        self.container = container

    async def get_tasks_by_assignee(self, assignee_id: str):
        query = "SELECT * FROM c WHERE c.assigneeId = @assigneeId"
        params = [{"name": "@assigneeId", "value": assignee_id}]
        items = []
        async for item in self.container.query_items(
            query=query, parameters=params, partition_key=assignee_id
        ):
            items.append(item)
        return items
