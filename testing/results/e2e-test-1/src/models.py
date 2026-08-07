from pydantic import BaseModel, Field
from typing import Optional
import uuid


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""  # partition key = user_id (same as id for users), set after creation
    username: str
    email: str
    type: str = "user"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # partition key
    title: str
    description: str = ""
    completed: bool = False
    type: str = "task"


class CreateUserRequest(BaseModel):
    username: str
    email: str


class CreateTaskRequest(BaseModel):
    title: str
    description: str = ""


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
