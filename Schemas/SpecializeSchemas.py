from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class InviteCreate(BaseModel):
    team_id: UUID


class InviteRead(BaseModel):
    id: UUID
    team_id: UUID
    expires_at: datetime
    is_used: bool

    class Config:
        from_attributes = True


class ActivityRead(BaseModel):
    id: UUID
    action_type: str
    resource_id: UUID
    resource_type: str
    timestamp: datetime
    user_id: UUID

    class Config:
        from_attributes = True
