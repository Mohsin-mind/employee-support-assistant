#!/usr/bin/env python3
"""Backend application entrypoint.

Automatically resolves repository root onto sys.path and boots Uvicorn server
with settings loaded from backend.app.core.config.
Can be executed from repository root or from within the backend/ directory.
"""
import sys
from pathlib import Path

# Automatically ensure repository root is in sys.path
CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parent
REPO_ROOT = BACKEND_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if __name__ == "__main__":
    import uvicorn
    from backend.app.core.config import settings

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
