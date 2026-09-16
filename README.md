# AI Employee Assistant

A learning project that builds an AI employee assistant from scratch and progressively introduces **RAG, LangChain, and LangGraph**.

---

## Quickstart: Running the Application

### Prerequisites
- **PostgreSQL**: Running on `localhost:5432` with database `employee_support_assistant` and user credentials configured in `backend/.env`.
- **Node.js**: v20+ & **pnpm**: v9+
- **Python**: 3.8+

---

### 1. Start the Backend Server (FastAPI)

The backend runs on **port 3001** with hot reloading enabled:

```bash
# Navigate to backend directory
cd backend

# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
source venv/bin/activate        # On Ubuntu / Linux / macOS
# . venv/Scripts/activate       # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python app.py
```

- **API Base URL**: `http://localhost:3001`
- **Health Check Endpoint**: [http://localhost:3001/api/v1/health](http://localhost:3001/api/v1/health)
- **Interactive Swagger Docs**: [http://localhost:3001/api/v1/docs](http://localhost:3001/api/v1/docs)

---

### 2. Start the Frontend Server (Vite + React + Tailwind v4)

Open a new terminal window to start the client on **port 3000**:

```bash
# Navigate to frontend directory
cd frontend

# 1. Install dependencies
pnpm install

# 2. Start dev server
pnpm dev
```

- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- *(Note: Vite automatically proxies all `/api` requests to the FastAPI backend at `http://localhost:3001`)*.

---

### 3. Verify System Health & Run Tests

```bash
# Run backend health & database connectivity tests (from backend/):
cd backend
python tests/unit/test_health.py

# Verify frontend TypeScript build (from frontend/):
cd frontend
pnpm run build
```

---

## Stack

### Frontend

* React
* Vite
* TypeScript
* Tailwind CSS v4
* TanStack Query
* React Hook Form
* Zod

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic

### Database

* PostgreSQL
* pgvector

### AI

* OpenAI / Gemini
* Embeddings
* RAG
* LangChain
* LangGraph

---

## Project Goal

Build an employee assistant that can:

* Answer questions from company documents
* Remember conversations
* Check leave balance
* Check calendar availability
* Apply for leave
* Handle multi-step requests with an AI agent

---

## Key Technical Features

* **Streaming First**: Real-time token streaming via Server-Sent Events (SSE).
* **Non-Blocking Ingestion**: Background tasks for document parsing, chunking, and embedding generation.
* **Optimized Vector Search**: PostgreSQL + `pgvector` accelerated with HNSW indexing.
* **Symmetric Validation**: Zod on the client matched with Pydantic v2 on the server.
* **Clean Layering**: Strict Router → Service → Repository pattern isolating business and AI logic.

---

## Development Approach

```text
Manual implementation
        ↓
Manual RAG
        ↓
Manual memory
        ↓
Manual tool calling
        ↓
LangChain
        ↓
LangChain Agent
        ↓
LangGraph Agent
```

The purpose is to understand **what each AI technology does and what problem it solves**, rather than only using frameworks without understanding the underlying implementation.

---

## Roadmap & Phases

See the detailed 9-phase guide in [DEVELOPMENT_PHASES.md](DEVELOPMENT_PHASES.md).
