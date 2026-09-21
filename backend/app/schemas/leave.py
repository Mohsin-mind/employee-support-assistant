from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from backend.app.core.constants import LeaveType, LeaveStatus


class LeaveBalanceCreate(BaseModel):
    """Payload to assign or initialize leave balance for an employee."""
    employee_id: int = Field(..., gt=0, description="Target employee ID")
    leave_type: LeaveType = Field(..., description="Category of leave")
    year: int = Field(..., ge=2000, le=2100, description="Calendar year")
    allocated_days: int = Field(..., ge=0, le=365, description="Total days allocated")
    used_days: int = Field(default=0, ge=0, le=365, description="Days already used")


class LeaveBalanceUpdate(BaseModel):
    """Payload to adjust existing leave balance."""
    allocated_days: Optional[int] = Field(None, ge=0, le=365)
    used_days: Optional[int] = Field(None, ge=0, le=365)


class LeaveBalanceResponse(BaseModel):
    """Response representation of employee leave balance."""
    id: int
    employee_id: int
    leave_type: LeaveType
    year: int
    allocated_days: int
    used_days: int
    remaining_days: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaveRequestCreate(BaseModel):
    """Payload to submit a new leave request."""
    employee_id: int = Field(..., gt=0, description="Requesting employee ID")
    leave_type: LeaveType = Field(..., description="Category of leave requested")
    start_date: date = Field(..., description="First day of leave")
    end_date: date = Field(..., description="Last day of leave (inclusive)")
    reason: str = Field(..., min_length=3, max_length=500, description="Reason for leave request")

    @model_validator(mode="after")
    def validate_dates(self) -> "LeaveRequestCreate":
        if self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")
        return self


class LeaveRequestStatusUpdate(BaseModel):
    """Payload for manager approval, rejection, or cancellation."""
    status: LeaveStatus = Field(..., description="New leave status")
    manager_note: Optional[str] = Field(None, max_length=500, description="Optional manager feedback")


class LeaveRequestResponse(BaseModel):
    """Response representation of a leave request."""
    id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    days: int
    reason: str
    status: LeaveStatus
    manager_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaveFilterParams(BaseModel):
    """Query filters for leave requests."""
    employee_id: Optional[int] = None
    status: Optional[LeaveStatus] = None
    leave_type: Optional[LeaveType] = None
    year: Optional[int] = None
