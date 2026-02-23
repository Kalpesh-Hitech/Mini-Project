from Core.Config.database import Base
import uuid
from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship



class InviteTokenDB(Base):
    __tablename__ = "invite_token"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=True
    )
    create_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    is_used: Mapped[bool] = mapped_column(default=False)

    teams: Mapped["TeamsDB"] = relationship("TeamsDB", back_populates="invites")
