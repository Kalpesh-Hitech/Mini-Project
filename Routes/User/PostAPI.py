from datetime import datetime, timedelta, timezone
import secrets
import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.config import settings
from Core.Config.database import async_get_db
from Models.InviteToken import InviteTokenDB
from Models.Teams import TeamsDB
from Models.UserTeams import UserTeamsDB
from Models.Users import UserDB
from Schemas.SpecializeSchemas import InviteCreate, InviteRead
from Schemas.UserSchemas import Login, UserCreate, UserLogin, UserRead, UserTeam
import uuid
from Utilies.auth import (
    RoleChecker,
    create_access_token,
    get_current_user,
    verify_password,
    hash_password,
)
from Utilies.helper import send_task_completion_email

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
    result = await db.execute(
        select(UserDB).where(UserDB.email == userseed.email, UserDB.is_active == True)
    )
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
        select(TeamsDB).where(
            TeamsDB.id == userteamseed.team_id, TeamsDB.is_deleted == False
        )
    )
    db_user_result = db_team.scalars().first()
    if not db_user_result:
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
        select(UserDB).where(
            UserDB.id == userteamseed.user_id, UserDB.is_active == True
        )
    )
    db_validate_user_result = db_validate_user.scalars().first()
    if not db_validate_user_result and db_validate_user_result.role != "employee":
        raise HTTPException(status_code=401, detail="user is not validate!!")
    query = select(UserTeamsDB).where(
        UserTeamsDB.user_id == userteamseed.user_id,
        UserTeamsDB.team_id == userteamseed.team_id,
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


@create_router.post("/create-invite", response_model=InviteRead)
async def create_invite_token(
    background_task: BackgroundTasks,
    data: InviteCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserDB = Depends(RoleChecker(["manager"])),
):

    team = await db.get(TeamsDB, data.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.create_by_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You can only create invite for your own team"
        )
    query = select(UserDB).where(
        UserDB.email == data.user_email, UserDB.role == "employee"
    )
    result = await db.execute(query)
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="email not found")
    query = select(UserTeamsDB).where(
        UserTeamsDB.user_id == db_user.id, UserTeamsDB.team_id == data.team_id
    )
    result = await db.execute(query)
    existing_membership = result.scalars().first()
    if existing_membership:
        raise HTTPException(
            status_code=400, detail="User is already a member of this team"
        )
    payload = {
        "sub": data.user_email,
        "team_id": str(data.team_id)
    }

    new_token_string= jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    invite = InviteTokenDB(
        team_id=data.team_id,
        create_by_id=current_user.id,
        token=new_token_string,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    background_task.add_task(
        send_task_completion_email, data.user_email, new_token_string
    )
    return invite

@create_router.get("/verify-invite/{token}")
async def verify_invite_token(token: str, db: AsyncSession = Depends(async_get_db)):
    query = select(InviteTokenDB).where(InviteTokenDB.token == token)
    result = await db.execute(query)
    invite = result.scalar_one_or_none()

    if not invite or invite.is_used:
        raise HTTPException(status_code=400, detail="Invalid or used invite")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        token_team_id = uuid.UUID(payload.get("team_id")) 
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid token data")

    user_query = select(UserDB).where(UserDB.email == email)
    user_result = await db.execute(user_query)
    db_user = user_result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id_to_add = db_user.id 

    new_membership = UserTeamsDB(
        user_id=user_id_to_add,
        team_id=token_team_id
    )
    
    invite.is_used = True
    db.add(new_membership)
    
    await db.commit()

    return {
        "status": "success",
        "user_id": user_id_to_add,
        "team_id": token_team_id
    }
