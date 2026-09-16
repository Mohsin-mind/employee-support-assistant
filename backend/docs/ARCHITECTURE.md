# Backend Architecture & Design Rules

This document defines the architectural standard, directory layout, layer boundaries, and request flows for the **Employee Support Assistant** backend.

---

## 1. Directory Structure

```text
backend/
├── app/
│   ├── main.py                     # Application factory, lifespan, CORS, exception handlers
│   │
│   ├── api/
│   │   ├── router.py               # Aggregates all route modules under /api/v1
│   │   ├── dependencies.py         # DB session (get_db), auth, common injections
│   │   └── routes/
│   │       ├── health.py           # Health check and DB connectivity status
│   │       ├── chat.py             # Chat sessions, streaming Q&A endpoints
│   │       ├── documents.py        # PDF upload, ingestion status, document management
│   │       ├── employees.py        # Employee profile and directory endpoints
│   │       └── leave.py            # Leave balance queries and leave applications
│   │
│   ├── core/
│   │   ├── config.py               # Pydantic BaseSettings (.env loading & validation)
│   │   ├── constants.py            # Global application constants and error codes
│   │   ├── helpers.py              # Timezone utilities, UUID generators
│   │   ├── logging.py              # Structured logging configuration
│   │   └── security.py             # Token generation, hashing, security utilities
│   │
│   ├── db/
│   │   ├── session.py              # Async SQLAlchemy engine & async_sessionmaker
│   │   ├── base.py                 # DeclarativeBase and TimestampMixin
│   │   └── models/
│   │       ├── employee.py         # Employee entity
│   │       ├── document.py         # Document metadata entity
│   │       ├── document_chunk.py   # Text chunk + pgvector embeddings entity
│   │       ├── conversation.py     # Conversation session entity
│   │       ├── conversation_message.py # Individual chat message entity
│   │       ├── leave_balance.py    # Leave balance allocation entity
│   │       └── leave_request.py    # Leave application / approval entity
│   │
│   ├── schemas/
│   │   ├── common.py               # BaseResponse, APIResponse, ErrorDetail, Pagination
│   │   ├── employee.py             # Employee request/response schemas
│   │   ├── chat.py                 # Chat request/response schemas & streaming payloads
│   │   ├── document.py             # Document upload, chunking, and search schemas
│   │   └── leave.py                # Leave request creation, balance response schemas
│   │
│   ├── repositories/
│   │   ├── employee_repository.py  # Employee database operations
│   │   ├── document_repository.py  # Documents and vector chunks database operations
│   │   ├── conversation_repository.py # Chat history database operations
│   │   └── leave_repository.py     # Leave balances and requests database operations
│   │
│   ├── services/
│   │   ├── chat_service.py         # Chat orchestration, history + RAG coordination
│   │   ├── document_service.py     # Document upload, parsing, and chunking service
│   │   ├── embedding_service.py    # Text embedding computation service
│   │   ├── retrieval_service.py    # Vector similarity search service
│   │   └── leave_service.py        # Leave validation and transaction business logic
│   │
│   ├── ai/                         # Isolated AI subsystem
│   │   ├── clients/
│   │   │   ├── llm.py              # LLM client abstractions (OpenAI / Gemini)
│   │   │   └── embeddings.py       # Embedding model client abstraction
│   │   │
│   │   ├── prompts/
│   │   │   ├── rag.py              # RAG context and system prompts
│   │   │   └── leave_agent.py      # Agent system instructions
│   │   │
│   │   ├── rag/
│   │   │   ├── chunking.py         # Text chunking logic
│   │   │   ├── ingestion.py        # PDF text extraction and chunk ingestion
│   │   │   └── retrieval.py        # Cosine distance retrieval against pgvector
│   │   │
│   │   ├── tools/                  # Deterministic tools callable by LLM
│   │   │   ├── get_leave_balance.py# Tool: fetch employee leave balance
│   │   │   ├── check_calendar.py   # Tool: check team calendar availability
│   │   │   └── apply_leave.py      # Tool: submit leave application
│   │   │
│   │   ├── memory/
│   │   │   └── conversation.py     # Sliding window context & token budget manager
│   │   │
│   │   ├── chains/                 # Stage 2: LangChain LCEL chains
│   │   │   └── employee_rag.py
│   │   │
│   │   └── graphs/                 # Stage 3: LangGraph stateful multi-step agent
│   │       └── leave_agent.py
│   │
│   └── exceptions/
│       ├── exceptions.py           # Domain exceptions (AppException, NotFound, etc.)
│       └── handlers.py             # Global FastAPI exception handlers
│
├── migrations/                     # Alembic migration scripts
├── tests/
│   ├── unit/                       # Unit tests
│   └── integration/                # Integration tests
├── .env
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## 2. Request Lifecycles

### Standard CRUD Request Flow
```text
HTTP Request
    ↓
FastAPI Route (app/api/routes/)
    ↓
Pydantic Validation (app/schemas/)
    ↓
Service Layer (app/services/)
    ↓
Repository Layer (app/repositories/)
    ↓
SQLAlchemy 2.0 ORM (app/db/models/)
    ↓
PostgreSQL Database
```

### AI / Agent Request Flow
```text
Chat Route (POST /api/v1/chat)
    ↓
Pydantic Request Schema
    ↓
Chat Service (app/services/chat_service.py)
    ↓
AI / RAG / Agent Layer (app/ai/)
    ↓
Retriever / Tools / LLM
    ↓
Repository Layer (if DB access/persistence needed)
    ↓
Pydantic Response Schema (or SSE Token Stream)
    ↓
Client
```

---

## 3. Technology Mapping (Mental Model)

| Concept | Node / Express Equivalent | Python / FastAPI Equivalent |
| :--- | :--- | :--- |
| **Validation / Typing** | Joi / Zod | Pydantic v2 (`BaseModel`, `Field`) |
| **ORM Model** | Sequelize / Prisma Model | SQLAlchemy 2.0 Declarative Model (`Base`) |
| **Query Engine** | Sequelize / Prisma Client | SQLAlchemy `AsyncSession` |
| **Migrations** | Sequelize-CLI / Prisma Migrate | Alembic (`alembic -c backend/alembic.ini`) |
| **Routing** | Express `Router()` | FastAPI `APIRouter()` |
| **Middleware / Auth** | Express Middleware (`req, res, next`)| FastAPI `Depends()` & Starlette Middlewares |

---

## 4. Database Schema & Tables

1. **`employees`**: Employee profiles, roles, departments.
2. **`documents`**: Uploaded company policies and reference files.
3. **`document_chunks`**: Text segments and vector embeddings:
   - `id`: Primary key (UUID/BigInt)
   - `document_id`: Foreign key to `documents`
   - `content`: Chunk text
   - `embedding`: Vector (pgvector dimension, indexed with HNSW)
   - `page_number`: Source page in PDF
   - `chunk_index`: Sequence position
   - `metadata`: JSONB metadata
   - `created_at`: Timestamp
4. **`conversations`**: Active or historical chat sessions.
5. **`conversation_messages`**: Chat turns (`user`, `assistant`, `tool`).
6. **`leave_balances`**: Allocated, used, and remaining leaves per employee.
7. **`leave_requests`**: Applied leave requests with dates, reason, status (`pending`, `approved`, `rejected`).

---

## 5. Architectural Invariants (Do Not Violate)

1. **Strict Layering**: Routes MUST NEVER execute raw database queries. All database access flows through the Repository layer.
2. **Service Orchestration**: Business decisions and multi-repository coordination belong in the Service layer, not in Routes or Repositories.
3. **AI Isolation**: LLM provider SDKs (OpenAI, Gemini, LangChain) must reside solely within `app/ai/` and `app/services/`. Routes only accept schemas and return schemas or streams.
4. **Non-blocking Ingestion**: PDF parsing, chunking, and embedding generation must run in background tasks (`FastAPI BackgroundTasks`).
