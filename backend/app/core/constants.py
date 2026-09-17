from enum import Enum


class StrEnum(str, Enum):
    """String enumeration base class that serializes as string."""
    def __str__(self) -> str:
        return str(self.value)


# Global API Configuration
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Employee Support Assistant"


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


# Pagination Defaults
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class ErrorCode(StrEnum):
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"


class LeaveStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveType(StrEnum):
    ANNUAL = "annual"
    SICK = "sick"
    CASUAL = "casual"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    UNPAID = "unpaid"


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


# Standard Reusable Messages (Avoid hardcoding repetitive strings)
class Messages:
    SUCCESS = "Operation completed successfully."
    CREATED = "Resource created successfully."
    UPDATED = "Resource updated successfully."
    DELETED = "Resource deleted successfully."
    NOT_FOUND = "Requested resource was not found."
    DATABASE_UNAVAILABLE = "Database service is temporarily unavailable."
    INTERNAL_ERROR = "An unexpected error occurred. Please try again later."
