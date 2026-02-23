from pydantic import BaseModel, Field
from typing import List
from .TaskSchemas import TaskCreate


class TaskBulkCreate(BaseModel):
    tasks: List[TaskCreate]


class TaskStats(BaseModel):
    todo: int
    doing: int
    complete: int
    total: int
