from Core.Config.database import Base
import uuid
from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from Models.InviteToken import InviteTokenDB
# from Models.Task import TaskDB
# from Models.UserTeams import UserTeamsDB


class TeamsDB(Base):
    __tablename__ = "teams"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(20))
    create_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)

    userteams: Mapped["UserTeamsDB"] = relationship(
        "UserTeamsDB", back_populates="team"
    )

    task: Mapped["TaskDB"] = relationship("TaskDB", back_populates="teams")

    invites: Mapped["InviteTokenDB"] = relationship(
        "InviteTokenDB", back_populates="teams"
    )
