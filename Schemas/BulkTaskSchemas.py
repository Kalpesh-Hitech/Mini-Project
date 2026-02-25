from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from uuid import UUID

from Models.Task import PriorityBased, StatusBased
from Schemas.TaskSchemas import TaskCreate

class UpdateTask(BaseModel):
    task_id:UUID
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityBased] = None
    status: Optional[StatusBased] = None
    assignee_id: Optional[UUID] = None
 
 
class TaskBulkCreate(BaseModel):
    tasks: List[TaskCreate] = Field(..., min_length=1)
 
    @field_validator("tasks")
    def check_max_batch_size(cls, v: List[TaskCreate]) -> List[TaskCreate]:
        if len(v) > 50:
            raise ValueError("Bulk create limit is 50 tasks per request")
        return v
 
 
class TaskBulkDelete(BaseModel):
    task_ids: List[UUID] = Field(..., min_length=1)
 
    @field_validator("task_ids")
    def check_max_batch_size(cls, v: List[UUID]) -> List[UUID]:
        if len(v) > 50:
            raise ValueError("Bulk delete limit is 50 tasks per request")
        return v