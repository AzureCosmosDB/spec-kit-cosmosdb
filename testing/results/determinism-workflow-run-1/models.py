"""Domain models for the workflow system."""
from pydantic import BaseModel
from typing import Optional, List


class Project(BaseModel):
    id: str
    name: str
    description: str
    memberIds: List[str]
    createdAt: str
    updatedAt: str


class Task(BaseModel):
    id: str
    projectId: str
    type: str = "task"
    title: str
    description: str
    status: str  # backlog | todo | in_progress | in_review | done | blocked
    priority: str  # low | medium | high | critical
    assigneeId: str
    labels: List[str] = []
    createdBy: str
    createdAt: str
    updatedAt: str


class Comment(BaseModel):
    id: str
    projectId: str
    type: str = "comment"
    taskId: str
    authorId: str
    body: str
    createdAt: str
    editedAt: Optional[str] = None


class StatusHistory(BaseModel):
    id: str
    projectId: str
    type: str = "statusHistory"
    taskId: str
    fromStatus: str
    toStatus: str
    changedBy: str
    changedAt: str
    reason: Optional[str] = None


class Assignee(BaseModel):
    id: str
    name: str
    email: str
    avatarUrl: Optional[str] = None


class AssigneeTask(BaseModel):
    id: str
    assigneeId: str
    taskId: str
    projectId: str
    title: str
    status: str
    priority: str
    updatedAt: str
