from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.db.models.conversation import Conversation
from backend.app.db.models.conversation_message import ConversationMessage


class ConversationRepository:
    """Encapsulates all database operations for Conversation and Message entities."""

    async def get_by_id(self, session: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        """Fetch a conversation by primary key."""
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
        employee_id: Optional[int] = None,
    ) -> Tuple[List[Conversation], int]:
        """Retrieve paginated conversations, optionally filtered by employee."""
        query = select(Conversation)
        count_query = select(func.count(Conversation.id))

        if employee_id is not None:
            query = query.where(Conversation.employee_id == employee_id)
            count_query = count_query.where(Conversation.employee_id == employee_id)

        total_count = (await session.execute(count_query)).scalar() or 0
        items = (await session.execute(
            query.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)
        )).scalars().all()

        return list(items), total_count

    async def create(self, session: AsyncSession, conversation: Conversation) -> Conversation:
        """Persist a new conversation session."""
        session.add(conversation)
        await session.flush()
        await session.refresh(conversation)
        return conversation

    async def update(self, session: AsyncSession, conversation: Conversation) -> Conversation:
        """Update an existing conversation (e.g. title)."""
        await session.flush()
        await session.refresh(conversation)
        return conversation

    async def delete(self, session: AsyncSession, conversation: Conversation) -> None:
        """Delete a conversation and all cascaded messages."""
        await session.delete(conversation)
        await session.flush()

    async def add_message(
        self,
        session: AsyncSession,
        message: ConversationMessage
    ) -> ConversationMessage:
        """Persist a message to a conversation."""
        session.add(message)
        await session.flush()
        await session.refresh(message)
        return message

    async def get_messages(
        self,
        session: AsyncSession,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[ConversationMessage]:
        """Fetch chronological messages for a conversation session."""
        stmt = select(ConversationMessage).where(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.created_at.asc())
        if limit:
            stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())
