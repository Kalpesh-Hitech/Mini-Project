from typing import List

from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.database import async_get_db
from Models.Task import TaskDB
from Models.Users import UserDB
from Schemas.TaskSchemas import TaskCreate, TaskRead
from Utilies.auth import RoleChecker
task_post=APIRouter()

@task_post.post("/create_task",response_model=TaskRead)
async def create_task(taskseed:TaskCreate,user:UserDB=Depends(RoleChecker(["admin","manager"])),db:AsyncSession=Depends(async_get_db)):
    
    new_task = TaskDB(**taskseed.model_dump(),created_by_id=user.id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task

 
 
@task_post.post("/bulk-create", response_model=List[TaskRead])
async def bulk_create_tasks(
    tasks: List[TaskCreate],
    user: UserDB = Depends(RoleChecker(["admin", "manager"])),
    db: AsyncSession = Depends(async_get_db),
):
    if not tasks:
        raise HTTPException(status_code=400, detail="Task list cannot be empty")
 
    new_tasks = [TaskDB(**task.model_dump(), created_by_id=user.id) for task in tasks]
 
    try:
        db.add_all(new_tasks)
        await db.commit()
 
        for task in new_tasks:
            await db.refresh(task)
 
        return new_tasks
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Bulk upload failed")
 
