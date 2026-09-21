from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class EmployeeBase(BaseModel):
    """Shared properties for employee schemas."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Employee first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Employee last name")
    email: str = Field(..., pattern=EMAIL_REGEX, description="Unique employee corporate email address")
    department: str = Field(..., min_length=1, max_length=100, description="Assigned department")
    role: str = Field(..., min_length=1, max_length=100, description="Job title / role")


class EmployeeCreate(EmployeeBase):
    """Payload for creating a new employee."""
    is_active: bool = Field(default=True, description="Account active status")


class EmployeeUpdate(BaseModel):
    """Payload for updating an existing employee profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, pattern=EMAIL_REGEX)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    """Symmetric response representation of an employee."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeFilterParams(BaseModel):
    """Query parameters for filtering employee listings."""
    department: Optional[str] = None
    is_active: Optional[bool] = None
