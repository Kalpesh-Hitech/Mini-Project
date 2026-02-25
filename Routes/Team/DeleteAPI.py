from logging.config import dictConfig
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Core.Config.database import async_get_db
from Models.Teams import TeamsDB
from Models.UserTeams import UserTeamsDB
from Models.Users import UserDB, UserRole
from Schemas.TeamSchemas import TeamRead
from Utilies.auth import get_current_user

delete_teamrouter=APIRouter()

@delete_teamrouter.delete("/teams/{team_id}", response_model=dict)
async def get_team(
    team_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserDB = Depends(get_current_user),
):
    team = (
        await db.execute(
            select
            (TeamsDB).where(
                TeamsDB.id == team_id,
                TeamsDB.is_deleted == False,
            )
        )
    ).scalar_one_or_none()
 
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
 
    if current_user.role == UserRole.ADMIN or (current_user.role==UserRole.MANAGER and team.create_by_id==current_user.id):
        team.is_deleted=True
        await db.commit()
        return {"message":"deleted successfully"}
 
    raise HTTPException(status_code=403,detail="if you are manager then you only delete your team")
# @get_teamrouter.get("/all_teams")