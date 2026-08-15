"""Audit log model for tracking user actions."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AuditLog(Base):
    """Audit trail entry for tracking user actions across the platform."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Action type: upload, delete, query, agent_call",
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(50), comment="Resource type: document, conversation"
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column()
    details: Mapped[dict | None] = mapped_column(
        JSON, comment="Additional action details"
    )
    ip_address: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} at {self.created_at}>"
