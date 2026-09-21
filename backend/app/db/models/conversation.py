from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin
from backend.app.core.helpers import generate_uuid

if TYPE_CHECKING:
    from backend.app.db.models.employee import Employee
    from backend.app.db.models.conversation_message import ConversationMessage


class Conversation(Base, TimestampMixin):
    """Chat session entity representing an ongoing or archived conversation."""
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    employee_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        default="New Conversation",
        nullable=False
    )

    # Relationships
    employee: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        back_populates="conversations"
    )
    messages: Mapped[List["ConversationMessage"]] = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Conversation id='{self.id}' title='{self.title}' employee_id={self.employee_id}>"
