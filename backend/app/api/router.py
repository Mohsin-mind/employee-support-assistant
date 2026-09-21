from fastapi import APIRouter
from backend.app.api.routes import health, employees, leave, conversations, documents

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router)
api_router.include_router(employees.router)
api_router.include_router(leave.router)
api_router.include_router(conversations.router)
api_router.include_router(documents.router)
