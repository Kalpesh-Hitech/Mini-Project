from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional, List
from Models.Users import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = UserRole.EMPLOYEE


class UserRead(UserBase):
    id: UUID
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models
