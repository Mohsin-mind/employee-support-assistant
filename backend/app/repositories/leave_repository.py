from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from backend.app.db.models.leave_balance import LeaveBalance
from backend.app.db.models.leave_request import LeaveRequest
from backend.app.core.constants import LeaveType, LeaveStatus


class LeaveRepository:
    """Encapsulates all database operations for LeaveBalance and LeaveRequest entities."""

    # --- Leave Balances ---

    async def get_balance(
        self,
        session: AsyncSession,
        employee_id: int,
        leave_type: LeaveType,
        year: int
    ) -> Optional[LeaveBalance]:
        """Fetch leave balance for a specific employee, leave type, and year."""
        stmt = select(LeaveBalance).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type == leave_type,
            LeaveBalance.year == year
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_balances_by_employee(
        self,
        session: AsyncSession,
        employee_id: int,
        year: Optional[int] = None
    ) -> List[LeaveBalance]:
        """Fetch all leave balances for an employee, optionally filtered by year."""
        stmt = select(LeaveBalance).where(LeaveBalance.employee_id == employee_id)
        if year:
            stmt = stmt.where(LeaveBalance.year == year)
        result = await session.execute(stmt.order_by(LeaveBalance.year.desc(), LeaveBalance.leave_type.asc()))
        return list(result.scalars().all())

    async def create_balance(self, session: AsyncSession, balance: LeaveBalance) -> LeaveBalance:
        """Persist a new leave balance allocation."""
        session.add(balance)
        await session.flush()
        await session.refresh(balance)
        return balance

    async def update_balance(self, session: AsyncSession, balance: LeaveBalance) -> LeaveBalance:
        """Update an existing leave balance."""
        await session.flush()
        await session.refresh(balance)
        return balance

    # --- Leave Requests ---

    async def get_request_by_id(self, session: AsyncSession, request_id: int) -> Optional[LeaveRequest]:
        """Fetch a leave request by its primary key."""
        stmt = select(LeaveRequest).where(LeaveRequest.id == request_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_requests(
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
        query = select(LeaveRequest)
        count_query = select(func.count(LeaveRequest.id))

        if employee_id is not None:
            query = query.where(LeaveRequest.employee_id == employee_id)
            count_query = count_query.where(LeaveRequest.employee_id == employee_id)
        if status is not None:
            query = query.where(LeaveRequest.status == status)
            count_query = count_query.where(LeaveRequest.status == status)
        if leave_type is not None:
            query = query.where(LeaveRequest.leave_type == leave_type)
            count_query = count_query.where(LeaveRequest.leave_type == leave_type)
        if year is not None:
            query = query.where(extract("year", LeaveRequest.start_date) == year)
            count_query = count_query.where(extract("year", LeaveRequest.start_date) == year)

        total_count = (await session.execute(count_query)).scalar() or 0
        items = (await session.execute(
            query.order_by(LeaveRequest.created_at.desc()).offset(offset).limit(limit)
        )).scalars().all()

        return list(items), total_count

    async def create_request(self, session: AsyncSession, leave_request: LeaveRequest) -> LeaveRequest:
        """Persist a new leave application."""
        session.add(leave_request)
        await session.flush()
        await session.refresh(leave_request)
        return leave_request

    async def update_request(self, session: AsyncSession, leave_request: LeaveRequest) -> LeaveRequest:
        """Update an existing leave application."""
        await session.flush()
        await session.refresh(leave_request)
        return leave_request

    async def check_overlapping_request(
        self,
        session: AsyncSession,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if an active (pending or approved) leave request already exists for these dates."""
        stmt = select(LeaveRequest.id).where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
            and_(
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date
            )
        )
        if exclude_id is not None:
            stmt = stmt.where(LeaveRequest.id != exclude_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None
