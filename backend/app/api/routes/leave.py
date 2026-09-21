from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.dependencies import get_db
from backend.app.schemas.common import (
    APIResponse,
    PaginatedResponse,
    PaginationParams,
    success_response,
    paginated_response,
)
from backend.app.schemas.leave import (
    LeaveBalanceCreate,
    LeaveBalanceResponse,
    LeaveRequestCreate,
    LeaveRequestStatusUpdate,
    LeaveRequestResponse,
)
from backend.app.services.leave_service import LeaveService
from backend.app.core.constants import (
    Messages,
    LeaveStatus,
    LeaveType,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)

router = APIRouter(prefix="/leave", tags=["Leave Management"])
service = LeaveService()


@router.get("/balances/{employee_id}", response_model=APIResponse[List[LeaveBalanceResponse]])
async def get_leave_balances(
    employee_id: int,
    year: Optional[int] = Query(None, description="Optional year filter"),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[LeaveBalanceResponse]]:
    """Retrieve all leave balance allocations for an employee."""
    balances = await service.get_employee_balances(db, employee_id, year)
    data = [LeaveBalanceResponse.model_validate(b) for b in balances]
    return success_response(data=data)


@router.post("/balances", response_model=APIResponse[LeaveBalanceResponse])
async def set_leave_balance(
    payload: LeaveBalanceCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[LeaveBalanceResponse]:
    """Create or update leave balance for an employee."""
    balance = await service.set_leave_balance(db, payload)
    await db.commit()
    data = LeaveBalanceResponse.model_validate(balance)
    return success_response(data=data, message=Messages.SUCCESS)


@router.get("/requests", response_model=PaginatedResponse[LeaveRequestResponse])
async def list_leave_requests(
    page: int = Query(default=DEFAULT_PAGE, ge=1, description="Page number"),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    status: Optional[LeaveStatus] = Query(None, description="Filter by request status"),
    leave_type: Optional[LeaveType] = Query(None, description="Filter by leave type"),
    year: Optional[int] = Query(None, description="Filter by request year"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LeaveRequestResponse]:
    """Retrieve paginated leave requests with optional filters."""
    params = PaginationParams(page=page, page_size=page_size)
    items, total = await service.list_leave_requests(
        session=db,
        offset=params.offset,
        limit=params.page_size,
        employee_id=employee_id,
        status=status,
        leave_type=leave_type,
        year=year,
    )
    data = [LeaveRequestResponse.model_validate(req) for req in items]
    return paginated_response(
        items=data,
        total_items=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post(
    "/requests",
    response_model=APIResponse[LeaveRequestResponse],
    status_code=status.HTTP_201_CREATED,
)
async def submit_leave_request(
    payload: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[LeaveRequestResponse]:
    """Submit a new leave application with business days and balance validation."""
    created = await service.apply_leave(db, payload)
    await db.commit()
    data = LeaveRequestResponse.model_validate(created)
    return success_response(data=data, message=Messages.CREATED)


@router.get("/requests/{request_id}", response_model=APIResponse[LeaveRequestResponse])
async def get_leave_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[LeaveRequestResponse]:
    """Fetch details of a single leave request."""
    leave_req = await service.get_leave_request(db, request_id)
    data = LeaveRequestResponse.model_validate(leave_req)
    return success_response(data=data)


@router.patch("/requests/{request_id}/status", response_model=APIResponse[LeaveRequestResponse])
async def update_leave_status(
    request_id: int,
    payload: LeaveRequestStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[LeaveRequestResponse]:
    """Update leave request status (approve, reject, cancel) with balance adjustment."""
    updated = await service.update_leave_status(db, request_id, payload)
    await db.commit()
    data = LeaveRequestResponse.model_validate(updated)
    return success_response(data=data, message=Messages.UPDATED)
