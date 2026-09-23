from typing import List, Tuple, Optional
from pathlib import Path
from fastapi import UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.document import Document
from backend.app.db.models.document_chunk import DocumentChunk
from backend.app.schemas.document import DocumentCreate, DocumentChunkCreate
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.exceptions.exceptions import raise_not_found, raise_bad_request
from backend.app.core.constants import DocumentStatus
from backend.app.core.config import settings
from backend.app.core.helpers import generate_uuid
from backend.app.core.logging import logger
from backend.app.ai.rag.ingestion import process_document_ingestion


class DocumentService:
    """Service layer managing document metadata and ingested chunks."""

    def __init__(self, document_repo: Optional[DocumentRepository] = None):
        self.document_repo = document_repo or DocumentRepository()

    async def get_document_by_id(self, session: AsyncSession, document_id: str) -> Document:
        """Fetch document by ID or raise 404."""
        doc = await self.document_repo.get_by_id(session, document_id)
        if not doc:
            raise_not_found("Document", document_id)
        return doc

    async def list_documents(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
        status: Optional[DocumentStatus] = None,
    ) -> Tuple[List[Document], int]:
        """List documents with optional status filter and pagination."""
        return await self.document_repo.get_all(
            session=session,
            offset=offset,
            limit=limit,
            status=status,
        )

    async def create_document(
        self,
        session: AsyncSession,
        payload: DocumentCreate
    ) -> Document:
        """Register a new document record."""
        doc = Document(
            filename=payload.filename,
            file_path=payload.file_path,
            file_size_bytes=payload.file_size_bytes,
            status=DocumentStatus.PENDING,
            meta_data=payload.meta_data,
        )
        created = await self.document_repo.create(session, doc)
        logger.info(f"Registered document id='{created.id}' filename='{created.filename}'")
        return created

    async def update_status(
        self,
        session: AsyncSession,
        document_id: str,
        status: DocumentStatus,
        error_message: Optional[str] = None
    ) -> Document:
        """Update processing status of a document."""
        doc = await self.get_document_by_id(session, document_id)
        doc.status = status
        if error_message:
            doc.error_message = error_message
        return await self.document_repo.update(session, doc)

    async def delete_document(self, session: AsyncSession, document_id: str) -> None:
        """Delete document record and all associated chunks."""
        doc = await self.get_document_by_id(session, document_id)
        await self.document_repo.delete(session, doc)
        logger.info(f"Deleted document id='{document_id}'")

    async def add_chunks(
        self,
        session: AsyncSession,
        document_id: str,
        chunks_payload: List[DocumentChunkCreate]
    ) -> List[DocumentChunk]:
        """Persist chunks for a document."""
        await self.get_document_by_id(session, document_id)

        chunks = [
            DocumentChunk(
                document_id=document_id,
                content=cp.content,
                chunk_index=cp.chunk_index,
                page_number=cp.page_number,
                meta_data=cp.meta_data,
            )
            for cp in chunks_payload
        ]
        return await self.document_repo.add_chunks(session, chunks)

    async def get_chunks(
        self,
        session: AsyncSession,
        document_id: str
    ) -> List[DocumentChunk]:
        """Fetch all chunks belonging to a document."""
        await self.get_document_by_id(session, document_id)
        return await self.document_repo.get_chunks(session, document_id)

    async def upload_and_enqueue_document(
        self,
        session: AsyncSession,
        file: UploadFile,
        background_tasks: BackgroundTasks,
    ) -> Document:
        """
        Validate, save uploaded PDF file to disk, register Document entity with PENDING status,
        and schedule background extraction, chunking, and embedding ingestion.
        """
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise_bad_request("Only PDF files (.pdf) are supported.")

        content = await file.read()
        file_size = len(content)
        if file_size == 0:
            raise_bad_request("Uploaded file is empty.")

        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        doc_id = generate_uuid()
        clean_filename = Path(file.filename).name
        target_path = upload_dir / f"{doc_id}_{clean_filename}"

        target_path.write_bytes(content)

        doc = Document(
            id=doc_id,
            filename=clean_filename,
            file_path=str(target_path.resolve()),
            file_size_bytes=file_size,
            status=DocumentStatus.PENDING,
            meta_data={"content_type": file.content_type},
        )
        created = await self.document_repo.create(session, doc)
        logger.info(f"Saved uploaded PDF '{clean_filename}' ({file_size} bytes) with document_id='{doc_id}'")

        # Offload text extraction, chunking, and FastEmbed vectorization to background task
        background_tasks.add_task(
            process_document_ingestion,
            document_id=doc_id,
            file_path_str=str(target_path.resolve()),
        )

        return created

