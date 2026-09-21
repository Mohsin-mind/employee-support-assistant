from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.conversation import Conversation
from backend.app.db.models.conversation_message import ConversationMessage
from backend.app.schemas.chat import (
    ConversationCreate,
    ConversationUpdate,
    ConversationMessageCreate,
)
from backend.app.repositories.conversation_repository import ConversationRepository
from backend.app.repositories.employee_repository import EmployeeRepository
from backend.app.exceptions.exceptions import raise_not_found
from backend.app.core.logging import logger


class ChatService:
    """Service layer coordinating conversation sessions and message history."""

    def __init__(
        self,
        conversation_repo: Optional[ConversationRepository] = None,
        employee_repo: Optional[EmployeeRepository] = None,
    ):
        self.conversation_repo = conversation_repo or ConversationRepository()
        self.employee_repo = employee_repo or EmployeeRepository()

    async def create_conversation(
        self,
        session: AsyncSession,
        payload: ConversationCreate
    ) -> Conversation:
        """Create a new chat conversation session."""
        if payload.employee_id:
            employee = await self.employee_repo.get_by_id(session, payload.employee_id)
            if not employee:
                raise_not_found("Employee", payload.employee_id)

        conv = Conversation(
            employee_id=payload.employee_id,
            title=payload.title or "New Conversation",
        )
        created = await self.conversation_repo.create(session, conv)
        logger.info(f"Created conversation id='{created.id}' title='{created.title}'")
        return created

    async def get_conversation(
        self,
        session: AsyncSession,
        conversation_id: str
    ) -> Conversation:
        """Retrieve a conversation by ID or raise 404."""
        conv = await self.conversation_repo.get_by_id(session, conversation_id)
        if not conv:
            raise_not_found("Conversation", conversation_id)
        return conv

    async def list_conversations(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
        employee_id: Optional[int] = None,
    ) -> Tuple[List[Conversation], int]:
        """List conversations with optional employee filter and pagination."""
        return await self.conversation_repo.get_all(
            session=session,
            offset=offset,
            limit=limit,
            employee_id=employee_id,
        )

    async def update_conversation_title(
        self,
        session: AsyncSession,
        conversation_id: str,
        payload: ConversationUpdate
    ) -> Conversation:
        """Update conversation title."""
        conv = await self.get_conversation(session, conversation_id)
        conv.title = payload.title
        return await self.conversation_repo.update(session, conv)

    async def delete_conversation(
        self,
        session: AsyncSession,
        conversation_id: str
    ) -> None:
        """Delete conversation and all its messages."""
        conv = await self.get_conversation(session, conversation_id)
        await self.conversation_repo.delete(session, conv)
        logger.info(f"Deleted conversation id='{conversation_id}'")

    async def add_message(
        self,
        session: AsyncSession,
        conversation_id: str,
        payload: ConversationMessageCreate
    ) -> ConversationMessage:
        """Append a message turn to an existing conversation."""
        # Ensure conversation exists
        await self.get_conversation(session, conversation_id)

        msg = ConversationMessage(
            conversation_id=conversation_id,
            role=payload.role,
            content=payload.content,
            token_count=payload.token_count,
            meta_data=payload.meta_data,
        )
        created_msg = await self.conversation_repo.add_message(session, msg)
        return created_msg

    async def get_messages(
        self,
        session: AsyncSession,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[ConversationMessage]:
        """Fetch messages for a conversation."""
        await self.get_conversation(session, conversation_id)
        return await self.conversation_repo.get_messages(session, conversation_id, limit)
