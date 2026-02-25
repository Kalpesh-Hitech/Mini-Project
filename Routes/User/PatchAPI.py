from pydantic._internal._decorators import RootValidatorDecoratorInfo
from fastapi import HTTPException
from uuid import UUID
from Core.Config.database import async_get_db
from Models.Users import UserDB
from Schemas.UserSchemas import UpdateUser, UserRead
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from Utilies.auth import RoleChecker
 
 
userUpdateRouter = APIRouter()
 
 
@userUpdateRouter.patch("/update-user", response_model=UserRead)
async def update_user(
    update_data: UpdateUser,
    user: UserDB = Depends(RoleChecker(["admin", "manager", "employee"])),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(UserDB).where(UserDB.id == update_data.user_id)
    result = await db.execute(query)
    result = result.scalars().first()
 
    if not result:
        raise HTTPException(status_code=404, detail="user nhi h")
 
    if user.role != "admin" and update_data.role is not None:
        raise HTTPException(status_code=403, detail="sirf admin role change krega")
 
    if result.role == "admin":
        raise HTTPException(status_code=400, detail="admin ka role change nhi karna")
 
    if result.role == update_data.role:
        raise HTTPException(status_code=400, detail="already same role me h")
 
    if result.role == "manager" and update_data.role == "user":
        raise HTTPException(status_code=400, detail="manager ko user nhi bana sakte")
 
    if result.role == "manager" and update_data.role == "admin":
        raise HTTPException(status_code=400, detail="manager ko admin nhi bana sakte")
   
    if user.role in ["admin","manager"] and update_data.role!="admin":
        if update_data.is_active is not None:
            result.is_active=update_data.is_active
   
   
    if update_data.user_id==user.id and update_data.name:
        result.name=update_data.name
   
    if update_data.role:
        result.role=update_data.role
    await db.commit()
    await db.refresh(result)
    return result