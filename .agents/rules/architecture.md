# System Architecture & Development Rules

This repository implements the **Employee Support Assistant** following strict architectural separation of concerns and progressive AI development. All AI agents and developers working on this repository must adhere to the patterns defined here.

## 1. End-to-End System Pattern

```text
React/Vite + Zod → FastAPI + Pydantic → Service Layer → Repository Layer → SQLAlchemy / PostgreSQL
```

- **Backend**: Strict **Router → Service → Repository → DB** layering. No raw SQL or repository queries inside route handlers.
- **Frontend**: **TanStack Query** for server state, **React Hook Form + Zod** for forms, **Axios** for HTTP, **React Router** for routing, and **Vanilla CSS** (`frontend/src/index.css`) for styling.
- **AI Evolution Roadmap**:
  ```text
  Phase 3: Manual RAG (Chunking + Embeddings + pgvector HNSW)
      ↓
  Phase 4: Manual Memory (Context Sliding Window + SSE Token Streaming)
      ↓
  Phase 5: Manual Tool Calling (Model Function Calling)
      ↓
  Phase 6: LangChain RAG Migration (LCEL Chains)
      ↓
  Phase 7: LangChain Agent & Tools
      ↓
  Phase 8: LangGraph Stateful Agent (Multi-step with Approval Gates)
  ```

## 2. Invariants & Code Placement Rules

1. **Backend**:
   - Routes belong in `backend/app/api/routes/`.
   - Data validation and serialization models belong in `backend/app/schemas/` (Pydantic v2).
   - Business orchestration belongs in `backend/app/services/`.
   - Direct database interactions belong in `backend/app/repositories/`.
   - Database tables belong in `backend/app/db/models/` (SQLAlchemy 2.0).
   - AI logic (prompts, tools, chunking, chains, graphs) belongs in `backend/app/ai/`.

2. **Frontend**:
   - HTTP fetchers belong in `frontend/src/api/`.
   - Reusable UI primitives belong in `frontend/src/components/common/`.
   - Domain UI components belong in `frontend/src/components/{chat,documents,leave}/`.
   - Zod validation schemas belong in `frontend/src/schemas/` and must match backend Pydantic models.
   - Styling must use existing design tokens in `frontend/src/index.css`. Do NOT install TailwindCSS unless explicitly requested.

3. **Detailed Documentation References**:
   - Backend Architecture: `backend/docs/ARCHITECTURE.md`
   - Frontend Architecture: `frontend/docs/ARCHITECTURE.md`
   - Development Roadmap: `DEVELOPMENT_PHASES.md`
