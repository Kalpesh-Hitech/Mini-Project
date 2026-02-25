
from fastapi import HTTPException
from uuid import UUID
from Models.Users import UserDB
from Schemas.UserSchemas import UserRead
from Utilies.auth import RoleChecker
from fastapi import APIRouter, Depends
from Core.Config.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

 
 
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
 