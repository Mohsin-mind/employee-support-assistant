from fastapi import APIRouter, status
from backend.app.core.config import settings
from backend.app.db.session import check_database_connection
from backend.app.schemas.common import HealthResponse, HealthData
from backend.app.core.logging import logger

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def get_system_health():
    """Health check endpoint that verifies API and database status."""
    db_status = "disconnected"
    db_latency = None

    try:
        db_res = await check_database_connection()
        db_status = db_res.get("status", "connected")
        db_latency = db_res.get("latency_ms")
    except Exception as exc:
        logger.error(f"Health check failed to query database: {exc}", exc_info=True)
        db_status = f"error: {str(exc)}"

    is_healthy = db_status == "connected"

    return HealthResponse(
        success=is_healthy,
        data=HealthData(
            status="healthy" if is_healthy else "degraded",
            app_name=settings.APP_NAME,
            environment=settings.ENVIRONMENT,
            database=db_status,
            db_name=settings.DB_DATABASE,
            db_host=settings.DB_HOST_NAME,
            db_latency_ms=db_latency,
        )
    )
