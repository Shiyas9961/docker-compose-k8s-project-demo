from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    completed: bool | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    completed: bool
    created_at: datetime


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    count: int
    handled_by: str


class TaskOperationResponse(BaseModel):
    task: TaskResponse
    message: str
    handled_by: str


class MessageResponse(BaseModel):
    message: str
    handled_by: str


class HealthResponse(BaseModel):
    status: str
    application: str
    environment: str
    handled_by: str
    database: str
