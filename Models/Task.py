import enum

from pydantic import BaseModel
import uuid
from Core.Config.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, String, UUID

# from Models.Teams import TeamsDB
# from Models.Users import UserDB


class PriorityBased(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StatusBased(str, enum.Enum):
    TODO = "todo"
    DOING = "doing"
    COMPLETE = "complete"


class TaskDB(Base):
    __tablename__ = "tasks"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    title: Mapped[int] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(100), nullable=True)
    priority: Mapped[PriorityBased] = mapped_column(
        Enum(PriorityBased), default=PriorityBased.MEDIUM
    )
    status: Mapped[StatusBased] = mapped_column(
        Enum(StatusBased), default=StatusBased.TODO
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL"), nullable=True
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    assign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    is_deleted: Mapped[bool] = mapped_column(default=False)

    teams: Mapped["TeamsDB"] = relationship("TeamsDB", back_populates="task")

    creator: Mapped["UserDB"] = relationship("UserDB",foreign_keys="TaskDB.created_by_id", back_populates="manager_task")

    assignee: Mapped["UserDB"] = relationship("UserDB",foreign_keys="TaskDB.assign_id", back_populates="user_task")
