from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    create_by_id: Optional[UUID]=None


class TeamUpdate(BaseModel):
    name: Optional[str] = None


class TeamRead(TeamBase):
    id: UUID
    create_by_id: UUID
    is_deleted: bool

    class Config:
        from_attributes = True
