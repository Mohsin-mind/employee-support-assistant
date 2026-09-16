from typing import Generic, Optional, TypeVar, Any, List
from pydantic import BaseModel, Field
from backend.app.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, Messages

DataT = TypeVar("DataT")


# --- Base Response Envelopes ---

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = Messages.SUCCESS


class APIResponse(BaseResponse, Generic[DataT]):
    data: Optional[DataT] = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


# --- Pagination Envelopes ---

class PaginationParams(BaseModel):
    page: int = Field(default=DEFAULT_PAGE, ge=1, description="Page number starting at 1")
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Number of items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedData(BaseModel, Generic[DataT]):
    items: List[DataT]
    pagination: PageMeta


class PaginatedResponse(BaseResponse, Generic[DataT]):
    data: PaginatedData[DataT]


# --- Common Response Factory Helpers ---

def success_response(data: Optional[DataT] = None, message: str = Messages.SUCCESS) -> APIResponse[DataT]:
    """Helper to build a uniform success APIResponse."""
    return APIResponse(success=True, message=message, data=data)


def paginated_response(
    items: List[DataT],
    total_items: int,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    message: str = Messages.SUCCESS,
) -> PaginatedResponse[DataT]:
    """Helper to build a uniform PaginatedResponse with computed metadata."""
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
    return PaginatedResponse(
        success=True,
        message=message,
        data=PaginatedData(
            items=items,
            pagination=PageMeta(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1,
            ),
        ),
    )


# --- Health Schemas ---

class HealthData(BaseModel):
    status: str = Field(..., description="Overall system health: healthy or degraded")
    app_name: str
    environment: str
    database: str = Field(..., description="Database connection status: connected or disconnected")
    db_name: str
    db_host: str
    db_latency_ms: Optional[float] = None


class HealthResponse(BaseModel):
    success: bool = True
    data: HealthData
