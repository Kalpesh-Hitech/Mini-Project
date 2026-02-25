
from fastapi import HTTPException
from uuid import UUID
from Models.Task import StatusBased, TaskDB
from Models.Teams import TeamsDB
from Models.UserTeams import UserTeamsDB
from Models.Users import UserDB, UserRole
from Schemas.UserSchemas import UserRead
from Utilies.auth import RoleChecker, get_current_user
from fastapi import APIRouter, Depends
from Core.Config.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

 
 
userRouter = APIRouter()
 
 
@userRouter.get("/me", response_model=UserRead)
async def get_me(
    user: UserDB = Depends(RoleChecker(["admin", "manager", "user"])),
    db: AsyncSession = Depends(async_get_db),
):
    return user
 
 
@userRouter.get("/all", response_model=list[UserRead])
async def get_all_users(
    user: UserDB = Depends(RoleChecker(["admin"])),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(UserDB)
    result = await db.execute(query)
    result = result.scalars().all()
    return result
 
 
@userRouter.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: UUID,
    user: UserDB = Depends(RoleChecker(["admin", "manager"])),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(UserDB).where(UserDB.id == user_id,UserDB.is_active==True)
    result = await db.execute(query)
    result = result.scalars().first()
 
    if not result:
        raise HTTPException(status_code=404, detail="user nhi h")
    return result
 
@userRouter.get("/tasks/stats")
async def get_task_stats(
    db: AsyncSession = Depends(async_get_db),
    current_user: UserDB = Depends(get_current_user),
):
    base_query = select(TaskDB.status, func.count(TaskDB.id)).where(
        TaskDB.is_deleted == False
    )
 
    if current_user.role == UserRole.ADMIN:
        query = base_query.group_by(TaskDB.status)
 
    elif current_user.role == UserRole.MANAGER:
        subquery = select(TeamsDB.id).where(
            TeamsDB.create_by_id == current_user.id,
            TeamsDB.is_deleted == False,
        )
 
        query = (
            base_query
            .where(TaskDB.team_id.in_(subquery))
            .group_by(TaskDB.status)
        )
 
    else:
        subquery = select(UserTeamsDB.team_id).where(
            UserTeamsDB.user_id == current_user.id
        )
 
        query = (
            base_query
            .where(TaskDB.team_id.in_(subquery))
            .group_by(TaskDB.status)
        )
 
    result = await db.execute(query)
    rows = result.all()
 
    stats = {status.name: 0 for status in StatusBased}
 
    for status, count in rows:
        stats[status.name] = count
 
    return stats