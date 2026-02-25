from typing import List

from fastapi import APIRouter, BackgroundTasks,Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.database import async_get_db
from Models.Task import TaskDB
from Models.Teams import TeamsDB
from Models.Users import UserDB
from Schemas.BulkTaskSchemas import UpdateTask
from Schemas.TaskSchemas import TaskCreate, TaskRead, TaskUpdate, TaskUpdateAssign
from Utilies.auth import RoleChecker
from Utilies.helper import send_task_completion_email
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
@task_patch.patch("/update-task", response_model=TaskRead)
async def updatetask(
    background_tasks: BackgroundTasks,
    task_data: TaskUpdate,
    user: UserDB = Depends(RoleChecker(["admin", "manager", "employee"])),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(TaskDB).where(
        TaskDB.id == task_data.task_id, TaskDB.is_deleted == False
    )
    existing_record = await db.execute(query)
    existing_record = existing_record.scalars().first()

    if not existing_record:
        raise HTTPException(status_code=404, detail="task nhi h")

    if existing_record.created_by_id != user.id and user.role == "manager":
        raise HTTPException(
            status_code=403, detail="apna task dekho bhai, dusre me nhi aana"
        )
    if (
        task_data.status
        and task_data.status.lower() == "complete"
        and existing_record.status != "complete"
        and user.role == "employee"
    ):
        user_email = user.email
        task_title = task_data.title or existing_record.title
        background_tasks.add_task(
            send_task_completion_email, user.email, existing_record.title
        )
        print(f"DEBUG: Email task added for {user_email} regarding {task_title}")
    if user.role == "admin" or user.role == "manager":
        if task_data.title:
            existing_record.title = task_data.title
        if task_data.description:
            existing_record.description = task_data.description
        if task_data.priority:
            existing_record.priority = task_data.priority
        if task_data.assign_id:
            existing_record.assignee_id = task_data.assign_id
    if task_data.status:
        existing_record.status = task_data.status
    await db.commit()
    await db.refresh(existing_record)
    return existing_record

@task_patch.patch("/bulk-update", response_model=List[TaskRead])
async def bulk_update_tasks(
    updates: List[UpdateTask],
    user: UserDB = Depends(RoleChecker(["admin", "manager"])),
    db: AsyncSession = Depends(async_get_db),
):
    if not updates:
        raise HTTPException(status_code=400, detail="Update list cannot be empty")
 
    task_ids = [u.task_id for u in updates]
    query = select(TaskDB).where(TaskDB.id.in_(task_ids))
    result = await db.execute(query)
    existing_tasks = {t.id: t for t in result.scalars().all()}
 
    if len(existing_tasks) != len(task_ids):
        raise HTTPException(status_code=404, detail="Kuch task IDs database mein nahi mile")
 
    updated_objects = []
    for update_data in updates:
        target_task = existing_tasks.get(update_data.task_id)
 
        if user.role == "manager" and target_task.created_by_id != user.id:
            raise HTTPException(
                status_code=403,
                detail=f"Task {target_task.id} aapki nahi hai, update nahi kar sakte"
            )
 
        update_dict = update_data.model_dump(exclude_unset=True, exclude={"task_id"})
        for key, value in update_dict.items():
            setattr(target_task, key, value)
 
        updated_objects.append(target_task)
 
    try:
        await db.commit()
        for t in updated_objects:
            await db.refresh(t)
        return updated_objects
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Bulk update failed")
 