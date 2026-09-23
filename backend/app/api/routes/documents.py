from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.dependencies import get_db
from backend.app.schemas.common import (
    APIResponse,
    PaginatedResponse,
    PaginationParams,
    success_response,
    paginated_response,
)
from backend.app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentDetailResponse,
    DocumentChunkResponse,
)
from backend.app.services.document_service import DocumentService
from backend.app.core.constants import (
    Messages,
    DocumentStatus,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)

router = APIRouter(prefix="/documents", tags=["Documents"])
service = DocumentService()


@router.get("", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    page: int = Query(default=DEFAULT_PAGE, ge=1, description="Page number"),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
    status_filter: Optional[DocumentStatus] = Query(None, alias="status", description="Filter by status"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DocumentResponse]:
    """Retrieve paginated list of uploaded documents."""
    params = PaginationParams(page=page, page_size=page_size)
    items, total = await service.list_documents(
        session=db,
        offset=params.offset,
        limit=params.page_size,
        status=status_filter,
    )
    data = [DocumentResponse.model_validate(d) for d in items]
    return paginated_response(
        items=data,
        total_items=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post(
    "",
    response_model=APIResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    payload: DocumentCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DocumentResponse]:
    """Register a new document record."""
    doc = await service.create_document(db, payload)
    await db.commit()
    data = DocumentResponse.model_validate(doc)
    return success_response(data=data, message=Messages.CREATED)


@router.get("/{document_id}", response_model=APIResponse[DocumentDetailResponse])
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DocumentDetailResponse]:
    """Fetch document details including ingested chunks."""
    doc = await service.get_document_by_id(db, document_id)
    data = DocumentDetailResponse.model_validate(doc)
    return success_response(data=data)


@router.delete("/{document_id}", response_model=APIResponse[None])
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    """Delete a document and all its chunks."""
    await service.delete_document(db, document_id)
    await db.commit()
    return success_response(data=None, message=Messages.DELETED)


@router.post(
    "/upload",
    response_model=APIResponse[DocumentResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF document file to upload and index"),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DocumentResponse]:
    """
    Upload a PDF policy document. Text extraction, chunking, and FastEmbed
    vector indexing run asynchronously via BackgroundTasks.
    """
    doc = await service.upload_and_enqueue_document(
        session=db,
        file=file,
        background_tasks=background_tasks,
    )
    await db.commit()
    data = DocumentResponse.model_validate(doc)
    return success_response(
        data=data,
        message="Document uploaded and queued for background indexing.",
    )


@router.get(
    "/{document_id}/chunks",
    response_model=APIResponse[List[DocumentChunkResponse]],
)
async def get_document_chunks(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[DocumentChunkResponse]]:
    """Retrieve all text chunks and page mappings for an ingested document."""
    chunks = await service.get_chunks(db, document_id)
    data = [DocumentChunkResponse.model_validate(c) for c in chunks]
    return success_response(data=data)

