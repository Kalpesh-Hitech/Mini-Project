from datetime import UTC, datetime

from Core.Config.database import Base
import uuid
from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from Models.Teams import TeamsDB
# from Models.Users import UserDB


class UserTeamsDB(Base):
    __tablename__ = "userteams"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE")
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))

    user: Mapped["UserDB"] = relationship("UserDB", back_populates="userteams")
    team: Mapped["TeamsDB"] = relationship("TeamsDB", back_populates="userteams")
