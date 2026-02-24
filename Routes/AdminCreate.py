from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.database import async_get_db
from Models.Users import UserDB
from Utilies.auth import hash_password
admin_router=APIRouter()

@admin_router.post("/create_admin")
async def create_admin(db:AsyncSession=Depends(async_get_db)):
    admin=UserDB(name="kalpesh",email="kalpesh13@gmail.com",role="admin")
    hashed_password=hash_password("123456789")
    admin.password=hashed_password
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(admin)

    return admin    