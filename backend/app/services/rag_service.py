from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.rag import RAGQueryRequest, RAGQueryResponse, CitedChunk
from backend.app.ai.rag.retrieval import retrieve_relevant_chunks
from backend.app.ai.prompts.rag import RAG_SYSTEM_PROMPT, format_rag_user_prompt
from backend.app.ai.clients.llm import llm_client, GroqLLMClient
from backend.app.core.logging import logger


class RAGService:
    """Service orchestrating semantic retrieval, grounded prompt construction, and Groq LLM inference."""

    def __init__(self, client: Optional[GroqLLMClient] = None):
        self.llm = client or llm_client

    async def query(
        self,
        session: AsyncSession,
        request: RAGQueryRequest,
    ) -> RAGQueryResponse:
        """
        Execute manual RAG pipeline without LangChain:
        1. Query embedding & pgvector similarity search
        2. Format grounded context with citations
        3. Groq LLM answer generation
        """
        logger.info(f"Processing RAG query: '{request.query}' (top_k={request.top_k})")

        # 1. Retrieve top-k relevant chunks from pgvector
        chunk_results = await retrieve_relevant_chunks(
            session=session,
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
        )

        # 2. Build citations list
        sources = [
            CitedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_name=filename,
                page_number=chunk.page_number,
                content=chunk.content,
                similarity=score,
            )
            for chunk, score, filename in chunk_results
        ]

        # 3. Construct grounded prompt
        user_prompt = format_rag_user_prompt(request.query, chunk_results)
        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # 4. Generate response via Groq LLM
        answer = await self.llm.generate_completion(messages=messages)

        logger.info(f"RAG query answered successfully with {len(sources)} source citations.")
        return RAGQueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
        )
