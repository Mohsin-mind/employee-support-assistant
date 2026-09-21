from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin
from backend.app.core.constants import LeaveType

if TYPE_CHECKING:
    from backend.app.db.models.employee import Employee


class LeaveBalance(Base, TimestampMixin):
    """Employee leave balance allocation per leave type and year."""
    __tablename__ = "leave_balances"
    __table_args__ = (
        UniqueConstraint("employee_id", "leave_type", "year", name="uq_employee_leave_type_year"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    leave_type: Mapped[LeaveType] = mapped_column(
        SQLEnum(LeaveType, native_enum=False, length=50),
        nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    allocated_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    used_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="leave_balances"
    )

    @property
    def remaining_days(self) -> int:
        return max(0, self.allocated_days - self.used_days)

    def __repr__(self) -> str:
        return (
            f"<LeaveBalance id={self.id} employee_id={self.employee_id} "
            f"type={self.leave_type} year={self.year} remaining={self.remaining_days}>"
        )
