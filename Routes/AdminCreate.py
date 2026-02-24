from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.database import async_get_db
from Models.Users import UserDB
admin_router=APIRouter()

@admin_router.post("/create_admin")
async def create_admin(db:AsyncSession=Depends(async_get_db)):
    admin=UserDB(name="kalpesh",email="kalpesh123@gmail.com",password="123456789",role="admin")
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    return admin    