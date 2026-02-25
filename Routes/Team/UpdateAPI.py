from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.database import async_get_db
from Models.Teams import TeamsDB
from Models.UserTeams import UserTeamsDB
from Models.Users import UserDB
from Schemas.TeamSchemas import TeamCreate, TeamRead, TeamUpdate, UpdateTeamRead
from Utilies.auth import RoleChecker

team_patch = APIRouter()


@team_patch.patch("/update_team", response_model=TeamRead)
async def create_team(
    teamseed: TeamUpdate,
    user: UserDB = Depends(RoleChecker(["admin", "manager"])),
    db: AsyncSession = Depends(async_get_db),
):
    query=select(TeamsDB).where(TeamsDB.id==teamseed.team_id,TeamsDB.is_deleted==False)
    result = await db.execute(query)
    db_user=result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404,detail="id is not found!!")
    if user.role!="admin":
        if db_user.create_by_id!=user.id:
            raise HTTPException(status_code=403,detail="you can change only your team name")
    db_user.name=teamseed.name
    await db.commit()
    await db.refresh(db_user)
    return db_user
