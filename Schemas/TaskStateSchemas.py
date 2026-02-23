from pydantic import BaseModel, Field,field_validator
from typing import List
from .TaskSchemas import TaskCreate


class TaskBulkCreate(BaseModel):
    tasks: List[TaskCreate]
    @field_validator("tasks")
    def check_max_batch_size(cls, v: List[TaskCreate]) -> List[TaskCreate]:
        if len(v) > 50:
            raise ValueError("Bulk create limit is 50 tasks per request")
        return v

class TaskStats(BaseModel):
    todo: int
    doing: int
    complete: int
    total: int
