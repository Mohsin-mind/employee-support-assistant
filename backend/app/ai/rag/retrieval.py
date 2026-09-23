from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.document_chunk import DocumentChunk
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.ai.clients.embeddings import embedding_client
from backend.app.core.logging import logger

_document_repo = DocumentRepository()


async def retrieve_relevant_chunks(
    session: AsyncSession,
    query: str,
    top_k: int = 4,
    document_id: Optional[str] = None,
) -> List[Tuple[DocumentChunk, float, str]]:
    """
    Generate embedding for the user query and retrieve top_k most similar
    document chunks from pgvector using cosine distance.

    Returns:
        List of tuples: (DocumentChunk, similarity_score, document_filename)
    """
    logger.info(f"Retrieving top {top_k} chunks for query: '{query[:60]}...'")

    # 1. Generate query embedding via FastEmbed
    query_embedding = embedding_client.embed_query(query)

    # 2. Perform vector search in PostgreSQL
    results = await _document_repo.search_similar_chunks(
        session=session,
        query_embedding=query_embedding,
        top_k=top_k,
        document_id=document_id,
    )

    logger.info(f"Retrieved {len(results)} chunks (highest similarity: {results[0][1] if results else 0.0})")
    return results
