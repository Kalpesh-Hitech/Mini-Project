import enum

from sqlalchemy import Boolean, Enum, String, UUID
import uuid
from Core.Config.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from Models.ActivityLog import ActivityLogDB
# from Models.Task import TaskDB
# from Models.UserTeams import UserTeamsDB


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class UserDB(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name: Mapped[String] = mapped_column(String(20))
    email: Mapped[String] = mapped_column(String(50), unique=True)
    password: Mapped[String] = mapped_column(String(200))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    is_active: Mapped[bool] = mapped_column(default=True)

    userteams: Mapped["UserTeamsDB"] = relationship(
        "UserTeamsDB", back_populates="user"
    )

    manager_task: Mapped["TaskDB"] = relationship("TaskDB", back_populates="creator")

    user_task: Mapped["TaskDB"] = relationship("TaskDB", back_populates="assignee")

    activities: Mapped["ActivityLogDB"] = relationship(
        "ActivityLogDB", back_populates="user"
    )
