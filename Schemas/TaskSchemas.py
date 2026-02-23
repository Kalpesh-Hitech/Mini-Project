from Models.Task import PriorityBased, StatusBased
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityBased = PriorityBased.MEDIUM
    status: StatusBased = StatusBased.TODO


class TaskCreate(TaskBase):
    team_id: UUID
    assignee_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityBased] = None
    status: Optional[StatusBased] = None
    assignee_id: Optional[UUID] = None


class TaskRead(TaskBase):
    id: UUID
    team_id: Optional[UUID]
    created_by_id: UUID
    assignee_id: Optional[UUID]
    is_deleted: bool

    class Config:
        from_attributes = True
