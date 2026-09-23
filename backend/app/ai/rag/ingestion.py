from pathlib import Path
from typing import List, Tuple
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import AsyncSessionLocal
from backend.app.db.models.document import Document
from backend.app.db.models.document_chunk import DocumentChunk
from backend.app.core.constants import DocumentStatus
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.ai.rag.chunking import split_pages_into_chunks
from backend.app.ai.clients.embeddings import embedding_client


def extract_pdf_pages(file_path: Path) -> List[Tuple[int, str]]:
    """
    Extract text page-by-page from a PDF file.
    Returns a list of (page_number, text) tuples (1-indexed).
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    reader = PdfReader(str(file_path))
    pages: List[Tuple[int, str]] = []

    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((idx, text))

    return pages


async def process_document_ingestion(document_id: str, file_path_str: str) -> None:
    """
    Background worker that extracts, chunks, embeds, and indexes a PDF document in pgvector.
    """
    file_path = Path(file_path_str)
    logger.info(f"Starting background ingestion for document_id='{document_id}' ({file_path.name})")

    async with AsyncSessionLocal() as session:
        # 1. Mark document as PROCESSING
        doc = await session.get(Document, document_id)
        if not doc:
            logger.error(f"Ingestion failed: Document '{document_id}' not found.")
            return

        doc.status = DocumentStatus.PROCESSING
        await session.commit()

        try:
            # 2. Extract text page-by-page
            pages = extract_pdf_pages(file_path)
            if not pages:
                raise ValueError("No extractable text found in PDF document.")

            # 3. Split into overlapping chunks with page metadata
            chunks = split_pages_into_chunks(
                pages=pages,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
            )
            if not chunks:
                raise ValueError("Document yielded zero text chunks.")

            logger.info(f"Document '{document_id}' split into {len(chunks)} chunks across {len(pages)} pages.")

            # 4. Generate embeddings in batch via FastEmbed
            chunk_texts = [c.content for c in chunks]
            embeddings = embedding_client.embed_batch(chunk_texts)

            # 5. Persist chunks and vectors to pgvector
            db_chunks = [
                DocumentChunk(
                    document_id=document_id,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    embedding=embeddings[i],
                    meta_data=chunk.metadata,
                )
                for i, chunk in enumerate(chunks)
            ]

            session.add_all(db_chunks)

            # 6. Mark document as INDEXED
            doc = await session.get(Document, document_id)
            if doc:
                doc.status = DocumentStatus.INDEXED
                doc.error_message = None

            await session.commit()
            logger.info(f"Document '{document_id}' successfully indexed with {len(db_chunks)} chunks.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Ingestion failed for document '{document_id}': {e}", exc_info=True)

            # Mark as FAILED
            async with AsyncSessionLocal() as error_session:
                doc_to_fail = await error_session.get(Document, document_id)
                if doc_to_fail:
                    doc_to_fail.status = DocumentStatus.FAILED
                    doc_to_fail.error_message = str(e)
                    await error_session.commit()
