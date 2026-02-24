from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from typing import Optional, List
from Models.Users import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str

    @field_validator("name")
    def name_must_not_be_empty(cls, v: str) -> str:
        cleaned_name = v.strip()
        if not cleaned_name:
            raise ValueError("Name cannot be empty or just whitespace")
        return cleaned_name


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = UserRole.EMPLOYEE

    @field_validator("password")
    def password_strength(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr]=None
    name: Optional[str]=None
    password: Optional[str]= Field(..., min_length=8)
    role: Optional[UserRole] = UserRole.EMPLOYEE
    is_active:Optional[bool]=None

class UserRead(UserBase):
    id: UUID
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True 
