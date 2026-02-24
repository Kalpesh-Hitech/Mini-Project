from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Core.Config.database import async_get_db
from Models.Teams import TeamsDB
from Models.UserTeams import UserTeamsDB
from Models.Users import UserDB
from Schemas.TeamSchemas import TeamCreate, TeamRead
from Utilies.auth import RoleChecker

team_post = APIRouter()


@team_post.post("/create_team", response_model=TeamRead)
async def create_team(
    teamseed: TeamCreate,
    user: UserDB = Depends(RoleChecker(["admin", "manager"])),
    db: AsyncSession = Depends(async_get_db),
):
    team_data = teamseed.model_dump(exclude={"create_by_id"})

    if user.role == "admin":
        if teamseed.create_by_id is None:
            raise HTTPException(status_code=400, detail="Admins must specify a manager ID")
        
        creator_id = teamseed.create_by_id

    else:
        creator_id = user.id

    new_team = TeamsDB(**team_data, create_by_id=creator_id)
    
    db.add(new_team)
    await db.flush() 

    new_user_team = UserTeamsDB(
        user_id=creator_id,
        team_id=new_team.id
    )
    db.add(new_user_team)
    
    await db.commit()
    await db.refresh(new_team)

    return new_team
