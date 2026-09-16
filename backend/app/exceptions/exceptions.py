from typing import Any, Optional, NoReturn
from backend.app.core.constants import ErrorCode, Messages


class AppException(Exception):
    """Base application exception with status_code, error_code, and details."""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = ErrorCode.INTERNAL_ERROR,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message: str = Messages.NOT_FOUND, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code=ErrorCode.NOT_FOUND,
            details=details
        )


class BadRequestException(AppException):
    def __init__(self, message: str = "Invalid request payload", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code=ErrorCode.BAD_REQUEST,
            details=details
        )


class ConflictException(AppException):
    def __init__(self, message: str = "Resource conflict occurred", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code=ErrorCode.CONFLICT,
            details=details
        )


class DatabaseConnectionException(AppException):
    def __init__(self, message: str = Messages.DATABASE_UNAVAILABLE, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=503,
            error_code=ErrorCode.DATABASE_UNAVAILABLE,
            details=details
        )


class AIServiceException(AppException):
    def __init__(self, message: str = "AI service invocation failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=502,
            error_code=ErrorCode.AI_SERVICE_ERROR,
            details=details
        )


# --- Common Exception Raiser Helpers ---

def raise_not_found(entity_name: str, identifier: Any) -> NoReturn:
    """Convenience helper to raise a formatted NotFoundException."""
    raise NotFoundException(
        message=f"{entity_name} with identifier '{identifier}' was not found.",
        details={"entity": entity_name, "identifier": str(identifier)}
    )


def raise_bad_request(message: str, details: Optional[Any] = None) -> NoReturn:
    """Convenience helper to raise a BadRequestException."""
    raise BadRequestException(message=message, details=details)


def raise_conflict(message: str, details: Optional[Any] = None) -> NoReturn:
    """Convenience helper to raise a ConflictException."""
    raise ConflictException(message=message, details=details)
