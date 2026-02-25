from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    create_by_id: Optional[UUID]=None


class TeamUpdate(BaseModel):
    team_id:UUID
    name: Optional[str] = None


class TeamRead(TeamBase):
    id: UUID
    create_by_id: UUID
    
    is_deleted: bool

    class ConfigDict:
        from_attributes = True

class UpdateTeamRead(BaseModel):
    id: UUID
    title:str

from pydantic import BaseModel, EmailStr
from typing import List

class TeamMemberStats(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    task_count: int

class ManagerDetails(BaseModel):
    id: UUID
    name: str
    email: EmailStr

class TeamDetailResponse(BaseModel):
    team_id: UUID
    team_name: str
    task_count: int
    member_count: int
    manager: ManagerDetails
    members: List[TeamMemberStats]