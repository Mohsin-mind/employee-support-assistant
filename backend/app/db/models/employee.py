from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.app.db.models.leave_balance import LeaveBalance
    from backend.app.db.models.leave_request import LeaveRequest
    from backend.app.db.models.conversation import Conversation


class Employee(Base, TimestampMixin):
    """Employee profile entity."""
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    leave_balances: Mapped[List["LeaveBalance"]] = relationship(
        "LeaveBalance",
        back_populates="employee",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    leave_requests: Mapped[List["LeaveRequest"]] = relationship(
        "LeaveRequest",
        back_populates="employee",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="employee",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Employee id={self.id} email='{self.email}' name='{self.first_name} {self.last_name}'>"
