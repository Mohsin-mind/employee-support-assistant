from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class RAGQueryRequest(BaseModel):
    """Request payload for semantic search and grounded AI question answering."""
    query: str = Field(
        ...,
        min_length=2,
        max_length=1000,
        description="Employee question regarding company policies",
        examples=["What is the company policy on remote work and sick leave?"],
    )
    top_k: int = Field(
        default=4,
        ge=1,
        le=20,
        description="Maximum number of context chunks to retrieve for grounding",
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Filter retrieval to a specific document ID",
    )


class CitedChunk(BaseModel):
    """Citation metadata and content for a source chunk used to ground the LLM answer."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="ID of source document")
    document_name: str = Field(..., description="Filename of source document")
    page_number: Optional[int] = Field(None, description="PDF page number (1-indexed)")
    content: str = Field(..., description="Text content of the retrieved chunk")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score (0.0 to 1.0)")

    model_config = ConfigDict(from_attributes=True)


class RAGQueryResponse(BaseModel):
    """Response payload containing generated answer and source citations."""
    query: str = Field(..., description="Original user question")
    answer: str = Field(..., description="Grounded answer generated from policy documents")
    sources: List[CitedChunk] = Field(default_factory=list, description="Retrieved source chunks cited in the answer")
