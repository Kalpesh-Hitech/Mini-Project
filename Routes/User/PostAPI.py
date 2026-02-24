from hmac import new

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.database import async_get_db
from Models.Teams import TeamsDB
from Models.UserTeams import UserTeamsDB
from Models.Users import UserDB
from Schemas.UserSchemas import Login, UserCreate, UserLogin, UserRead, UserTeam
from Utilies.auth import (
    RoleChecker,
    create_access_token,
    verify_password,
    hash_password,
)

create_router = APIRouter()


@create_router.post("/create_user", response_model=UserRead)
async def create_user(
    userseed: UserCreate,
    user: UserDB = Depends(RoleChecker(["admin", "manager"])),
    db: AsyncSession = Depends(async_get_db),
):
    if user.role == "manager" and (
        userseed.role == "manager" or userseed.role == "admin"
    ):
        raise HTTPException(
            status_code=403, detail="only admin can create the admin and manager"
        )
    hashed_password = hash_password(userseed.password)
    new_user = UserDB(
        name=userseed.name,
        email=userseed.email,
        password=hashed_password,
        role=userseed.role,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@create_router.post("/login", response_model=Login)
async def login(userseed: UserLogin, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(UserDB).where(UserDB.email == userseed.email))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user is not found!! ")
    if not verify_password(userseed.password, db_user.password):
        raise HTTPException(status_code=404, detail="password is incorrect!! ")
    token = create_access_token({"sub": db_user.email})
    return {"token": token}


@create_router.post("/assignee_teams")
async def assign_team_touser(
    userteamseed: UserTeam,
    user: UserDB = Depends(RoleChecker(["manager"])),
    db: AsyncSession = Depends(async_get_db),
):

    db_team = await db.execute(
        select(TeamsDB).where(TeamsDB.id == userteamseed.team_id)
    )
    db_user_result = db_team.scalars().first()
    if not  db_user_result:
        raise HTTPException(
            status_code=404,
            detail="ye team id galat hai!!",
        )
    if db_user_result.create_by_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only assign employees to your own team",
        )
    db_validate_user = await db.execute(
        select(UserDB).where(UserDB.id == userteamseed.user_id)
    )
    db_validate_user_result = db_validate_user.scalars().first()
    if not db_validate_user_result and db_validate_user_result.role != "employee":
        raise HTTPException(status_code=401, detail="user is not validate!!")
    query = select(UserTeamsDB).where(
        UserTeamsDB.user_id == userteamseed.user_id, UserTeamsDB.team_id == userteamseed.team_id
    )
    result = await db.execute(query)
    existing_record = result.scalars().first()
    if existing_record:
        raise HTTPException(status_code=400, detail="user pehle se team me h")
    new_userteam = UserTeamsDB(**userteamseed.model_dump())
    db.add(new_userteam)
    await db.commit()
    await db.refresh(new_userteam)

    return {"this user is assigned to team"}
