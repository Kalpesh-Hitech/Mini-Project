from datetime import UTC, datetime

from Core.Config.database import Base
import uuid
from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship



class ActivityLogDB(Base):
    __tablename__ = "activity_log"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    action_type: Mapped[String] = mapped_column(String(40))
    resource_id: Mapped[int] = mapped_column(nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda:datetime.now(UTC)
    )

    user: Mapped["UserDB"] = relationship("UserDB", back_populates="activities")
