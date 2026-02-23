from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None


class TeamRead(TeamBase):
    id: UUID
    created_by_id: UUID
    is_deleted: bool

    class Config:
        from_attributes = True
