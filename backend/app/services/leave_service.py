from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.leave_balance import LeaveBalance
from backend.app.db.models.leave_request import LeaveRequest
from backend.app.schemas.leave import (
    LeaveBalanceCreate,
    LeaveBalanceUpdate,
    LeaveRequestCreate,
    LeaveRequestStatusUpdate,
)
from backend.app.repositories.leave_repository import LeaveRepository
from backend.app.repositories.employee_repository import EmployeeRepository
from backend.app.exceptions.exceptions import raise_not_found, raise_bad_request, raise_conflict
from backend.app.core.constants import LeaveStatus, LeaveType
from backend.app.core.helpers import calculate_business_days
from backend.app.core.logging import logger


class LeaveService:
    """Domain business logic and validations for employee leave management."""

    def __init__(
        self,
        leave_repo: Optional[LeaveRepository] = None,
        employee_repo: Optional[EmployeeRepository] = None,
    ):
        self.leave_repo = leave_repo or LeaveRepository()
        self.employee_repo = employee_repo or EmployeeRepository()

    async def get_employee_balances(
        self,
        session: AsyncSession,
        employee_id: int,
        year: Optional[int] = None
    ) -> List[LeaveBalance]:
        """Fetch all leave balances for an employee, validating employee existence."""
        employee = await self.employee_repo.get_by_id(session, employee_id)
        if not employee:
            raise_not_found("Employee", employee_id)
        return await self.leave_repo.get_balances_by_employee(session, employee_id, year)

    async def set_leave_balance(
        self,
        session: AsyncSession,
        payload: LeaveBalanceCreate
    ) -> LeaveBalance:
        """Create or update a leave balance allocation."""
        employee = await self.employee_repo.get_by_id(session, payload.employee_id)
        if not employee:
            raise_not_found("Employee", payload.employee_id)

        existing = await self.leave_repo.get_balance(
            session, payload.employee_id, payload.leave_type, payload.year
        )
        if existing:
            existing.allocated_days = payload.allocated_days
            existing.used_days = payload.used_days
            return await self.leave_repo.update_balance(session, existing)

        balance = LeaveBalance(
            employee_id=payload.employee_id,
            leave_type=payload.leave_type,
            year=payload.year,
            allocated_days=payload.allocated_days,
            used_days=payload.used_days,
        )
        return await self.leave_repo.create_balance(session, balance)

    async def apply_leave(
        self,
        session: AsyncSession,
        payload: LeaveRequestCreate
    ) -> LeaveRequest:
        """Submit a leave application with business days and balance validation."""
        # 1. Verify employee exists and is active
        employee = await self.employee_repo.get_by_id(session, payload.employee_id)
        if not employee:
            raise_not_found("Employee", payload.employee_id)
        if not employee.is_active:
            raise_bad_request("Inactive employees cannot submit leave requests.")

        # 2. Date validation
        if payload.start_date > payload.end_date:
            raise_bad_request("Leave start date cannot be after end date.")

        # 3. Calculate business days
        requested_days = calculate_business_days(payload.start_date, payload.end_date)
        if requested_days <= 0:
            raise_bad_request("Leave duration must include at least one business day.")

        # 4. Check for overlapping active requests
        has_overlap = await self.leave_repo.check_overlapping_request(
            session, payload.employee_id, payload.start_date, payload.end_date
        )
        if has_overlap:
            raise_conflict("An active leave request already exists for overlapping dates.")

        # 5. Check leave balance for the requested year
        request_year = payload.start_date.year
        balance = await self.leave_repo.get_balance(
            session, payload.employee_id, payload.leave_type, request_year
        )
        if not balance:
            raise_bad_request(
                f"No {payload.leave_type.value} leave balance found for year {request_year}."
            )
        if balance.remaining_days < requested_days:
            raise_bad_request(
                f"Insufficient {payload.leave_type.value} leave balance. "
                f"Requested: {requested_days} business days, Remaining: {balance.remaining_days} days."
            )

        # 6. Create leave request
        request = LeaveRequest(
            employee_id=payload.employee_id,
            leave_type=payload.leave_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            days=requested_days,
            reason=payload.reason,
            status=LeaveStatus.PENDING,
        )
        created_request = await self.leave_repo.create_request(session, request)
        logger.info(
            f"Submitted leave request id={created_request.id} for employee_id={payload.employee_id} "
            f"({requested_days} days)"
        )
        return created_request

    async def get_leave_request(self, session: AsyncSession, request_id: int) -> LeaveRequest:
        """Fetch leave request by ID or raise 404."""
        request = await self.leave_repo.get_request_by_id(session, request_id)
        if not request:
            raise_not_found("LeaveRequest", request_id)
        return request

    async def list_leave_requests(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
        employee_id: Optional[int] = None,
        status: Optional[LeaveStatus] = None,
        leave_type: Optional[LeaveType] = None,
        year: Optional[int] = None,
    ) -> Tuple[List[LeaveRequest], int]:
        """Retrieve paginated leave requests with optional filters."""
        return await self.leave_repo.get_requests(
            session=session,
            offset=offset,
            limit=limit,
            employee_id=employee_id,
            status=status,
            leave_type=leave_type,
            year=year,
        )

    async def update_leave_status(
        self,
        session: AsyncSession,
        request_id: int,
        payload: LeaveRequestStatusUpdate
    ) -> LeaveRequest:
        """Process manager approval, rejection, or cancellation with balance reconciliation."""
        leave_req = await self.get_leave_request(session, request_id)
        old_status = leave_req.status
        new_status = payload.status

        if old_status == new_status:
            if payload.manager_note:
                leave_req.manager_note = payload.manager_note
                await self.leave_repo.update_request(session, leave_req)
            return leave_req

        request_year = leave_req.start_date.year
        balance = await self.leave_repo.get_balance(
            session, leave_req.employee_id, leave_req.leave_type, request_year
        )

        # Handle status transitions
        if new_status == LeaveStatus.APPROVED and old_status != LeaveStatus.APPROVED:
            if not balance or balance.remaining_days < leave_req.days:
                remaining = balance.remaining_days if balance else 0
                raise_bad_request(
                    f"Cannot approve: insufficient balance. Required: {leave_req.days}, Remaining: {remaining}."
                )
            balance.used_days += leave_req.days
            await self.leave_repo.update_balance(session, balance)

        elif old_status == LeaveStatus.APPROVED and new_status in (LeaveStatus.CANCELLED, LeaveStatus.REJECTED):
            if balance:
                balance.used_days = max(0, balance.used_days - leave_req.days)
                await self.leave_repo.update_balance(session, balance)

        leave_req.status = new_status
        if payload.manager_note:
            leave_req.manager_note = payload.manager_note

        updated = await self.leave_repo.update_request(session, leave_req)
        logger.info(f"Leave request id={request_id} transitioned from {old_status} to {new_status}")
        return updated
