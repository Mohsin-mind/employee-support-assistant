from datetime import datetime, timezone, date
from typing import List, TypeVar, Optional, Any
import uuid

T = TypeVar("T")


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a random UUID4 string."""
    return str(uuid.uuid4())


def format_iso_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime into ISO 8601 string."""
    if not dt:
        return None
    return dt.isoformat()


def calculate_business_days(start_date: date, end_date: date) -> int:
    """Calculate the number of business days (inclusive, excluding Sat/Sun)."""
    if start_date > end_date:
        return 0
    days = 0
    curr = start_date
    while curr <= end_date:
        if curr.weekday() < 5:  # Monday = 0, Friday = 4
            days += 1
        curr += datetime.resolution.days if hasattr(curr, 'days') else date.fromordinal(curr.toordinal() + 1)
    return days


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Safely truncate text with an ellipsis suffix."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into smaller chunks of size chunk_size."""
    if chunk_size <= 0:
        return [items]
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
