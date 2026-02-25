from Models.Task import PriorityBased, StatusBased
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityBased = PriorityBased.MEDIUM
    status: StatusBased = StatusBased.TODO

    @field_validator("title")
    def sanitize_title(cls, v: str) -> str:
        cleaned = v.capitalize()
        if not cleaned:
            raise ValueError("Title cannot be empty strings")
        return cleaned


class TaskCreate(TaskBase):
    team_id: Optional[UUID] = None
    assign_id: Optional[UUID] = None

class TaskUpdateAssign(BaseModel):
    task_id:UUID
    team_id:UUID
    assign_id:UUID

class TaskUpdate(BaseModel):
    task_id:UUID
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityBased] = None
    status: Optional[StatusBased] = None
    assign_id: Optional[UUID] = None


class TaskRead(TaskBase):
    id: UUID
    team_id: Optional[UUID]
    created_by_id: UUID
    assign_id: Optional[UUID]
    is_deleted: bool

    class Config:
        from_attributes = True
