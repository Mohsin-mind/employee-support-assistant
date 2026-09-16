#!/usr/bin/env python3
"""Backend application runner.

Allows running the FastAPI server directly via:
    python app.py
from inside the backend/ directory or from the repository root.
"""
import sys
from pathlib import Path

# Automatically ensure current directory and repository root are on sys.path
BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent

for path in (str(BACKEND_DIR), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import uvicorn
from backend.app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
