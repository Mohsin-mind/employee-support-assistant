from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.dependencies import get_db
from backend.app.schemas.common import APIResponse, success_response
from backend.app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from backend.app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])
rag_service = RAGService()


@router.post(
    "/query",
    response_model=APIResponse[RAGQueryResponse],
    summary="Query company policy documents via grounded RAG",
)
async def query_rag(
    payload: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[RAGQueryResponse]:
    """
    Submit an employee question to be answered by the Groq LLM grounded strictly
    in company policy PDF documents retrieved from pgvector.
    """
    result = await rag_service.query(session=db, request=payload)
    return success_response(data=result)
