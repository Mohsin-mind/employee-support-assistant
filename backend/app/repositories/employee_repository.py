from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.db.models.employee import Employee


class EmployeeRepository:
    """Encapsulates all database operations for Employee entities."""

    async def get_by_id(self, session: AsyncSession, employee_id: int) -> Optional[Employee]:
        """Fetch an employee by primary key."""
        stmt = select(Employee).where(Employee.id == employee_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[Employee]:
        """Fetch an employee by corporate email."""
        stmt = select(Employee).where(func.lower(Employee.email) == email.lower())
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Employee], int]:
        """Retrieve paginated employees with optional department and active status filters."""
        query = select(Employee)
        count_query = select(func.count(Employee.id))

        if department:
            query = query.where(Employee.department == department)
            count_query = count_query.where(Employee.department == department)
        if is_active is not None:
            query = query.where(Employee.is_active == is_active)
            count_query = count_query.where(Employee.is_active == is_active)

        total_count = (await session.execute(count_query)).scalar() or 0
        items = (await session.execute(query.order_by(Employee.id.asc()).offset(offset).limit(limit))).scalars().all()

        return list(items), total_count

    async def create(self, session: AsyncSession, employee: Employee) -> Employee:
        """Persist a new employee to the database."""
        session.add(employee)
        await session.flush()
        await session.refresh(employee)
        return employee

    async def update(self, session: AsyncSession, employee: Employee) -> Employee:
        """Update an existing employee."""
        await session.flush()
        await session.refresh(employee)
        return employee

    async def delete(self, session: AsyncSession, employee: Employee) -> None:
        """Delete an employee."""
        await session.delete(employee)
        await session.flush()
