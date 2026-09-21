# Employee Support Assistant — Architecture Overview

This project is an AI Employee Assistant designed with enterprise layering standards on both the backend and frontend, paired with a staged AI evolution roadmap.

## Global Request & Data Flow

```text
React/Vite (UI)
    ↓  (Axios HTTP request, validated by Zod)
FastAPI Route (backend/app/api/routes/)
    ↓  (Validated by Pydantic v2 schemas)
Service Layer (backend/app/services/)
    ↓  (Coordinates domain logic & AI subsystem)
Repository Layer (backend/app/repositories/)
    ↓  (Executes parameterized ORM queries)
SQLAlchemy 2.0 AsyncSession (backend/app/db/)
    ↓
PostgreSQL + pgvector (localhost:5432 / employee_support_assistant)
```

## AI Subsystem Flow

```text
Chat Route (/api/v1/chat)
    ↓
Chat Service (chat_service.py)
    ↓
AI Subsystem (backend/app/ai/)
    ├── RAG (chunking, ingestion, retrieval)
    ├── Tools (get_leave_balance, check_calendar, apply_leave)
    ├── Memory (token-budgeted sliding window)
    ├── Chains (LangChain LCEL)
    └── Graphs (LangGraph stateful workflow)
    ↓
Streaming Token Generator (Server-Sent Events)
    ↓
Frontend Chat Interface
```

## Subsystem Documentation

- **[Backend Architecture](/backend/docs/ARCHITECTURE.md)**: Layered layout, database tables, ORM models, and AI engine folder structure.
- **[Frontend Architecture](/frontend/docs/ARCHITECTURE.md)**: State management strategy, domain component structure, Zod-Pydantic symmetry, and design system.
- **[Development Phases](/DEVELOPMENT_PHASES.md)**: Progressive 9-phase implementation roadmap.
- **[AI System Rules](/.agents/rules/architecture.md)**: Persistent agent instructions preventing drift during automated coding.
