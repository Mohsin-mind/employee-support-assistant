from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.app.core.constants import DocumentStatus


class DocumentCreate(BaseModel):
    """Payload to register a new uploaded document."""
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_path: str = Field(..., min_length=1, max_length=1024, description="Local or object storage path")
    file_size_bytes: int = Field(..., gt=0, description="Size of file in bytes")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Arbitrary file metadata")


class DocumentChunkCreate(BaseModel):
    """Payload to store an individual text chunk of a document."""
    content: str = Field(..., min_length=1, description="Chunk textual content")
    chunk_index: int = Field(..., ge=0, description="Sequential index of chunk")
    page_number: Optional[int] = Field(None, ge=1, description="Original PDF page number")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Chunk metadata")


class DocumentChunkResponse(BaseModel):
    """Response representation of a document chunk."""
    id: str
    document_id: str
    content: str
    chunk_index: int
    page_number: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    """Response representation of an uploaded document."""
    id: str
    filename: str
    file_path: str
    file_size_bytes: int
    status: DocumentStatus
    error_message: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentResponse):
    """Detailed document response including ingested chunks."""
    chunks: List[DocumentChunkResponse] = []
