from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession

from Core.Config.database import async_get_db
from Models.Task import TaskDB
from Models.Teams import TeamsDB
from Models.UserTeams import UserTeamsDB
from Models.Users import UserDB, UserRole
from Schemas.TeamSchemas import ManagerDetails, TeamDetailResponse, TeamMemberStats, TeamRead
from Utilies.auth import get_current_user

get_teamrouter=APIRouter()

@get_teamrouter.get("/all_teams", response_model=list[TeamRead])
async def list_teams(
    db: AsyncSession = Depends(async_get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        teams = (
            (await db.execute(select(TeamsDB).where(TeamsDB.is_deleted == False)))
            .scalars()
            .all()
        )
        return teams
 
    if current_user.role == UserRole.MANAGER:
        teams = (
            (
                await db.execute(
                    select(TeamsDB).where(
                        TeamsDB.create_by_id == current_user.id,
                        TeamsDB.is_deleted == False,
                    )
                )
            )
            .scalars()
            .all()
        )
        return teams
 
    teams = (
        (
            await db.execute(
                select(TeamsDB)
                .join(UserTeamsDB, TeamsDB.id == UserTeamsDB.team_id)
                .where(
                    UserTeamsDB.user_id == current_user.id,
                    TeamsDB.is_deleted == False,
                )
            )
        )
        .scalars()
        .all()
    )
 
    return teams
 
 
@get_teamrouter.get("/teams/{team_id}", response_model=TeamDetailResponse)
async def get_team_details(
    team_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserDB = Depends(get_current_user),
):
    team = (
        await db.execute(
            select(TeamsDB).where(
                TeamsDB.id == team_id,
                TeamsDB.is_deleted == False,
            )
        )
    ).scalar_one_or_none()
 
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
 
    if current_user.role == UserRole.ADMIN:
        pass
 
    elif current_user.role == UserRole.MANAGER:
        if team.create_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        membership = (
            await db.execute(
                select(UserTeamsDB).where(
                    UserTeamsDB.team_id == team_id,
                    UserTeamsDB.user_id == current_user.id,
                )
            )
        ).scalar_one_or_none()
 
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied")
 
    task_count = (
        await db.execute(
            select(func.count(TaskDB.id)).where(
                TaskDB.team_id == team_id,
                TaskDB.is_deleted == False,
            )
        )
    ).scalar()
 
    member_count = (
        await db.execute(
            select(func.count(UserTeamsDB.user_id)).where(
                UserTeamsDB.team_id == team_id,
            )
        )
    ).scalar()
 
    manager = (
        await db.execute(select(UserDB).where(UserDB.id == team.create_by_id))
    ).scalar_one()
 
    members = (
        (
            await db.execute(
                select(UserDB)
                .join(UserTeamsDB, UserDB.id == UserTeamsDB.user_id)
                .where(UserTeamsDB.team_id == team_id)
            )
        )
        .scalars()
        .all()
    )
 
    members_data = []
 
    for member in members:
        user_task_count = (
            await db.execute(
                select(func.count(TaskDB.id)).where(
                    TaskDB.assign_id == member.id,
                    TaskDB.team_id == team_id,
                    TaskDB.is_deleted == False,
                )
            )
        ).scalar()
 
        members_data.append(
            TeamMemberStats(
                id=member.id,
                name=member.name,
                email=member.email,
                task_count=user_task_count,
            )
        )
 
    return TeamDetailResponse(
        team_id=team.id,
        team_name=team.name,
        task_count=task_count,
        member_count=member_count,
        manager=ManagerDetails(
            id=manager.id,
            name=manager.name,
            email=manager.email,
        ),
        members=members_data,
    )
# @get_teamrouter.get("/all_teams")