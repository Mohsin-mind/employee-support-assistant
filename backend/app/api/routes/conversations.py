from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.dependencies import get_db
from backend.app.schemas.common import (
    APIResponse,
    PaginatedResponse,
    PaginationParams,
    success_response,
    paginated_response,
)
from backend.app.schemas.chat import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationMessageCreate,
    ConversationMessageResponse,
)
from backend.app.services.chat_service import ChatService
from backend.app.core.constants import Messages, DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/conversations", tags=["Conversations"])
service = ChatService()


@router.get("", response_model=PaginatedResponse[ConversationResponse])
async def list_conversations(
    page: int = Query(default=DEFAULT_PAGE, ge=1, description="Page number"),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ConversationResponse]:
    """Retrieve paginated list of conversations."""
    params = PaginationParams(page=page, page_size=page_size)
    items, total = await service.list_conversations(
        session=db,
        offset=params.offset,
        limit=params.page_size,
        employee_id=employee_id,
    )
    data = [ConversationResponse.model_validate(c) for c in items]
    return paginated_response(
        items=data,
        total_items=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post(
    "",
    response_model=APIResponse[ConversationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConversationResponse]:
    """Initiate a new conversation session."""
    conv = await service.create_conversation(db, payload)
    await db.commit()
    data = ConversationResponse.model_validate(conv)
    return success_response(data=data, message=Messages.CREATED)


@router.get("/{conversation_id}", response_model=APIResponse[ConversationDetailResponse])
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConversationDetailResponse]:
    """Retrieve a conversation with its message history."""
    conv = await service.get_conversation(db, conversation_id)
    data = ConversationDetailResponse.model_validate(conv)
    return success_response(data=data)


@router.patch("/{conversation_id}", response_model=APIResponse[ConversationResponse])
async def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConversationResponse]:
    """Update conversation title."""
    updated = await service.update_conversation_title(db, conversation_id, payload)
    await db.commit()
    data = ConversationResponse.model_validate(updated)
    return success_response(data=data, message=Messages.UPDATED)


@router.delete("/{conversation_id}", response_model=APIResponse[None])
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    """Delete a conversation and all its messages."""
    await service.delete_conversation(db, conversation_id)
    await db.commit()
    return success_response(data=None, message=Messages.DELETED)


@router.post(
    "/{conversation_id}/messages",
    response_model=APIResponse[ConversationMessageResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    conversation_id: str,
    payload: ConversationMessageCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConversationMessageResponse]:
    """Append a message turn to an existing conversation."""
    msg = await service.add_message(db, conversation_id, payload)
    await db.commit()
    data = ConversationMessageResponse.model_validate(msg)
    return success_response(data=data, message=Messages.CREATED)


@router.get(
    "/{conversation_id}/messages",
    response_model=APIResponse[List[ConversationMessageResponse]],
)
async def list_messages(
    conversation_id: str,
    limit: Optional[int] = Query(None, ge=1, le=500, description="Optional message limit"),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[ConversationMessageResponse]]:
    """Retrieve chronological messages for a conversation session."""
    messages = await service.get_messages(db, conversation_id, limit)
    data = [ConversationMessageResponse.model_validate(m) for m in messages]
    return success_response(data=data)
