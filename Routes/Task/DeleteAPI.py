
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Core.Config.database import async_get_db
from Models.Task import TaskDB

from Models.Users import UserDB, UserRole
from Utilies.auth import get_current_user

delete_taskrouter=APIRouter()

@delete_taskrouter.delete("/task/{task_id}", response_model=dict)
async def get_team(
    task_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserDB = Depends(get_current_user),
):
    task = (
        await db.execute(
            select
            (TaskDB).where(
                TaskDB.id == task_id,
                TaskDB.is_deleted == False,
            )
        )
    ).scalar_one_or_none()
 
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
 
    if current_user.role == UserRole.ADMIN or (current_user.role==UserRole.MANAGER and task.created_by_id==current_user.id):
        task.is_deleted=True
        await db.commit()
        return {"message":"deleted successfully"}
 
    raise HTTPException(status_code=403,detail="if you are manager then you only delete your team")
# @get_teamrouter.get("/all_teams")