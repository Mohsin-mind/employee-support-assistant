.PHONY: help backend frontend dev test install

help:
	@echo "Employee Support Assistant - Development Commands:"
	@echo "  make backend   - Start FastAPI backend server on port 3001"
	@echo "  make frontend  - Start React Vite frontend dev server on port 3000"
	@echo "  make dev       - Run both backend and frontend servers in parallel"
	@echo "  make test      - Run backend unit tests"

backend:
	@./backend/.venv/bin/python backend/run.py

frontend:
	@npm --prefix frontend run dev

dev:
	@make -j 2 backend frontend

test:
	@PYTHONPATH=. ./backend/.venv/bin/python backend/tests/unit/test_health.py
