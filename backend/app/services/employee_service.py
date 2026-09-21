from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.employee import Employee
from backend.app.db.models.leave_balance import LeaveBalance
from backend.app.schemas.employee import EmployeeCreate, EmployeeUpdate
from backend.app.repositories.employee_repository import EmployeeRepository
from backend.app.repositories.leave_repository import LeaveRepository
from backend.app.exceptions.exceptions import raise_not_found, raise_conflict
from backend.app.core.constants import LeaveType
from backend.app.core.logging import logger


class EmployeeService:
    """Business logic and orchestration for Employee management."""

    def __init__(
        self,
        employee_repo: Optional[EmployeeRepository] = None,
        leave_repo: Optional[LeaveRepository] = None,
    ):
        self.employee_repo = employee_repo or EmployeeRepository()
        self.leave_repo = leave_repo or LeaveRepository()

    async def get_employee_by_id(self, session: AsyncSession, employee_id: int) -> Employee:
        """Fetch employee by ID or raise 404."""
        employee = await self.employee_repo.get_by_id(session, employee_id)
        if not employee:
            raise_not_found("Employee", employee_id)
        return employee

    async def list_employees(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Employee], int]:
        """List employees with optional filters and pagination."""
        return await self.employee_repo.get_all(
            session=session,
            offset=offset,
            limit=limit,
            department=department,
            is_active=is_active,
        )

    async def create_employee(self, session: AsyncSession, payload: EmployeeCreate) -> Employee:
        """Create a new employee and initialize default annual leave balances."""
        existing = await self.employee_repo.get_by_email(session, payload.email)
        if existing:
            raise_conflict(f"Employee with email '{payload.email}' already exists.")

        employee = Employee(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            department=payload.department,
            role=payload.role,
            is_active=payload.is_active,
        )
        created_employee = await self.employee_repo.create(session, employee)

        # Automatically allocate standard leave balances for the current year
        current_year = datetime.now().year
        default_balances = [
            (LeaveType.ANNUAL, 20),
            (LeaveType.SICK, 10),
            (LeaveType.CASUAL, 5),
        ]
        for leave_type, days in default_balances:
            bal = LeaveBalance(
                employee_id=created_employee.id,
                leave_type=leave_type,
                year=current_year,
                allocated_days=days,
                used_days=0,
            )
            await self.leave_repo.create_balance(session, bal)

        logger.info(f"Created employee id={created_employee.id} email='{created_employee.email}'")
        return created_employee

    async def update_employee(
        self,
        session: AsyncSession,
        employee_id: int,
        payload: EmployeeUpdate
    ) -> Employee:
        """Update employee details with duplicate email check."""
        employee = await self.get_employee_by_id(session, employee_id)

        update_data = payload.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"]:
            new_email = update_data["email"]
            if new_email.lower() != employee.email.lower():
                existing = await self.employee_repo.get_by_email(session, new_email)
                if existing:
                    raise_conflict(f"Email '{new_email}' is already in use by another employee.")

        for key, value in update_data.items():
            setattr(employee, key, value)

        return await self.employee_repo.update(session, employee)

    async def delete_employee(self, session: AsyncSession, employee_id: int) -> None:
        """Delete employee record."""
        employee = await self.get_employee_by_id(session, employee_id)
        await self.employee_repo.delete(session, employee)
        logger.info(f"Deleted employee id={employee_id}")
