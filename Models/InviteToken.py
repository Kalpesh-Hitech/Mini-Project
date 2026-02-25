from Core.Config.database import Base
import uuid
import secrets
from sqlalchemy import UUID, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta, timezone

class InviteTokenDB(Base):
    __tablename__ = "invite_token"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    
    token: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=True
    )
    
    create_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # Ensures timezone awareness in DB
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24)
    )
    
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)

    teams: Mapped["TeamsDB"] = relationship("TeamsDB", back_populates="invites")