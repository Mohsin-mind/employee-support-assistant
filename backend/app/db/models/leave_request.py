from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Enum as SQLEnum, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin
from backend.app.core.constants import LeaveType, LeaveStatus

if TYPE_CHECKING:
    from backend.app.db.models.employee import Employee


class LeaveRequest(Base, TimestampMixin):
    """Leave application submitted by an employee."""
    __tablename__ = "leave_requests"

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
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[LeaveStatus] = mapped_column(
        SQLEnum(LeaveStatus, native_enum=False, length=50),
        default=LeaveStatus.PENDING,
        nullable=False,
        index=True
    )
    manager_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="leave_requests"
    )

    def __repr__(self) -> str:
        return (
            f"<LeaveRequest id={self.id} employee_id={self.employee_id} "
            f"type={self.leave_type} days={self.days} status={self.status}>"
        )
