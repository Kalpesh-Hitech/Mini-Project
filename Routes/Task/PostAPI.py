from fastapi import APIRouter,Depends
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