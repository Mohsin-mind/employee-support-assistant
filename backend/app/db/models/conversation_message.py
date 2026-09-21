from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin
from backend.app.core.constants import MessageRole
from backend.app.core.helpers import generate_uuid

if TYPE_CHECKING:
    from backend.app.db.models.conversation import Conversation


class ConversationMessage(Base, TimestampMixin):
    """Individual chat turn within a conversation."""
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole, native_enum=False, length=50),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<ConversationMessage id='{self.id}' role={self.role} conversation_id='{self.conversation_id}'>"
