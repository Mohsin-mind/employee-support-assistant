from typing import Optional
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
from backend.app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)
from backend.app.services.employee_service import EmployeeService
from backend.app.core.constants import Messages, DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/employees", tags=["Employees"])
service = EmployeeService()


@router.get("", response_model=PaginatedResponse[EmployeeResponse])
async def list_employees(
    page: int = Query(default=DEFAULT_PAGE, ge=1, description="Page number"),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
    department: Optional[str] = Query(None, description="Filter by department"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[EmployeeResponse]:
    """Retrieve a paginated list of employees."""
    params = PaginationParams(page=page, page_size=page_size)
    items, total = await service.list_employees(
        session=db,
        offset=params.offset,
        limit=params.page_size,
        department=department,
        is_active=is_active,
    )
    data = [EmployeeResponse.model_validate(emp) for emp in items]
    return paginated_response(
        items=data,
        total_items=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post(
    "",
    response_model=APIResponse[EmployeeResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    payload: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[EmployeeResponse]:
    """Register a new employee and allocate initial annual leave balances."""
    employee = await service.create_employee(db, payload)
    await db.commit()
    data = EmployeeResponse.model_validate(employee)
    return success_response(data=data, message=Messages.CREATED)


@router.get("/{employee_id}", response_model=APIResponse[EmployeeResponse])
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[EmployeeResponse]:
    """Fetch employee profile by ID."""
    employee = await service.get_employee_by_id(db, employee_id)
    data = EmployeeResponse.model_validate(employee)
    return success_response(data=data)


@router.patch("/{employee_id}", response_model=APIResponse[EmployeeResponse])
async def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[EmployeeResponse]:
    """Update employee details."""
    updated = await service.update_employee(db, employee_id, payload)
    await db.commit()
    data = EmployeeResponse.model_validate(updated)
    return success_response(data=data, message=Messages.UPDATED)


@router.delete("/{employee_id}", response_model=APIResponse[None])
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    """Delete an employee."""
    await service.delete_employee(db, employee_id)
    await db.commit()
    return success_response(data=None, message=Messages.DELETED)
