
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from fastapi import BackgroundTasks
from Core.Config.database import async_get_db
from Models.Task import TaskDB
from Models.Users import UserDB
from Schemas.TaskSchemas import TaskRead, TaskUpdate
from Utilies.auth import RoleChecker
from sqlalchemy.ext.asyncio import AsyncSession

from Utilies.helper import send_task_completion_email

taskUpdateRouter=APIRouter()
@taskUpdateRouter.patch("/update-task", response_model=TaskRead)
async def update_task(
    background_tasks: BackgroundTasks,
    task_data:TaskUpdate ,
    user: UserDB = Depends(RoleChecker(["admin", "manager","employee"])),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(TaskDB).where(TaskDB.id == task_data.task_id,TaskDB.is_deleted==False)
    existing_record = await db.execute(query)
    existing_record = existing_record.scalars().first()
 
    if not existing_record:
        raise HTTPException(status_code=404, detail="task nhi h")
 
    if existing_record.created_by_id!=user.id and user.role=="manager":
        raise HTTPException(status_code=403, detail="apna task dekho bhai, dusre me nhi aana")
    if task_data.status and task_data.status.lower() == "complete" and existing_record.status != "complete" and user.role=="employee":
        # We send the mail to the user who created the task or the admin
        user_email = user.email 
        task_title = task_data.title or existing_record.title
        background_tasks.add_task(send_task_completion_email, user.email, existing_record.title)
        print(f"DEBUG: Email task added for {user_email} regarding {task_title}")
    if user.role=="admin" and user.role=="manager":
        if task_data.title:
            existing_record.title = task_data.title
        if task_data.description:
            existing_record.description = task_data.description
        if task_data.priority:
            existing_record.priority = task_data.priority
        if task_data.assign_id:
            existing_record.assignee_id=task_data.assign_id
    if task_data.status:
        existing_record.status = task_data.status
    await db.commit()
    await db.refresh(existing_record)
    return existing_record