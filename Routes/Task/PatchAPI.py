from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.database import async_get_db
from Models.Task import TaskDB
from Models.Teams import TeamsDB
from Models.Users import UserDB
from Schemas.TaskSchemas import TaskCreate, TaskRead, TaskUpdateAssign
from Utilies.auth import RoleChecker
task_patch=APIRouter()

@task_patch.patch("/assign_task",response_model=TaskRead)
async def assign_task(taskseed:TaskUpdateAssign,user:UserDB=Depends(RoleChecker(["manager"])),db:AsyncSession=Depends(async_get_db)):
    
    query = select(UserDB).where(
        UserDB.id==taskseed.assign_id,
        UserDB.is_active==True
    )
    result = await db.execute(query)
    existing_record = result.scalars().first()
    if not existing_record:
        raise HTTPException(status_code=404, detail="wrong assign id")
    query = select(TeamsDB).where(
        TeamsDB.id==taskseed.team_id,
        TeamsDB.is_deleted==False
    )
    result = await db.execute(query)
    existing_record = result.scalars().first()
    if not existing_record:
        raise HTTPException(status_code=404, detail="wrong team id")
    if existing_record.create_by_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only assign employees to your own team",
        )
    query = select(TaskDB).where(
        TaskDB.id==taskseed.task_id,
        TaskDB.is_deleted==False
    )
    result = await db.execute(query)
    existing_record = result.scalars().first()
    if not existing_record:
        raise HTTPException(status_code=404, detail="wrong task id")
    if existing_record.team_id is not None or existing_record.assign_id is not None:
        raise HTTPException(status_code=404, detail="task id have data ")
    existing_record.team_id=taskseed.team_id
    existing_record.assign_id=taskseed.assign_id
    await db.commit()

    return existing_record