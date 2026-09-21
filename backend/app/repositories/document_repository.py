from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.db.models.document import Document
from backend.app.db.models.document_chunk import DocumentChunk
from backend.app.core.constants import DocumentStatus


class DocumentRepository:
    """Encapsulates all database operations for Document and DocumentChunk entities."""

    async def get_by_id(self, session: AsyncSession, document_id: str) -> Optional[Document]:
        """Fetch a document by primary key."""
        stmt = select(Document).where(Document.id == document_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
        status: Optional[DocumentStatus] = None,
    ) -> Tuple[List[Document], int]:
        """Retrieve paginated documents with optional status filter."""
        query = select(Document)
        count_query = select(func.count(Document.id))

        if status is not None:
            query = query.where(Document.status == status)
            count_query = count_query.where(Document.status == status)

        total_count = (await session.execute(count_query)).scalar() or 0
        items = (await session.execute(
            query.order_by(Document.created_at.desc()).offset(offset).limit(limit)
        )).scalars().all()

        return list(items), total_count

    async def create(self, session: AsyncSession, document: Document) -> Document:
        """Persist a new document entity."""
        session.add(document)
        await session.flush()
        await session.refresh(document)
        return document

    async def update(self, session: AsyncSession, document: Document) -> Document:
        """Update an existing document."""
        await session.flush()
        await session.refresh(document)
        return document

    async def delete(self, session: AsyncSession, document: Document) -> None:
        """Delete a document and its cascaded chunks."""
        await session.delete(document)
        await session.flush()

    async def add_chunks(
        self,
        session: AsyncSession,
        chunks: List[DocumentChunk]
    ) -> List[DocumentChunk]:
        """Batch persist chunks for a document."""
        session.add_all(chunks)
        await session.flush()
        return chunks

    async def get_chunks(
        self,
        session: AsyncSession,
        document_id: str
    ) -> List[DocumentChunk]:
        """Fetch all chunks for a document in sequential chunk_index order."""
        stmt = select(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index.asc())
        result = await session.execute(stmt)
        return list(result.scalars().all())
