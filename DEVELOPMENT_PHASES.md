# Development Phases

## Phase 1 — Project Setup

Set up the basic application structure.

### Backend

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* Environment configuration
* Logging
* Error handling

### Frontend

* React
* Vite
* TypeScript
* React Router
* TanStack Query
* React Hook Form
* Zod

### Goal

Get the frontend and backend running with a working health-check API and database connection.

---

## Phase 2 — Database & Basic APIs

Build the normal application layer before adding AI.

### Implement

* Employee management
* Leave balance
* Leave requests
* Conversations
* Conversation messages
* Documents

### Architecture

```text
Route
  ↓
Pydantic Schema
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

### Goal

Understand the standard backend architecture independently of AI.

---

## Phase 3 — Manual PDF RAG

Build RAG **without LangChain**.

### Implement

```text
PDF Upload
 ↓
Extract text
 ↓
Split into chunks
 ↓
Background Task (Async Ingestion)
 ↓
Generate embeddings
 ↓
Store embeddings + text
 ↓
PostgreSQL + pgvector (with HNSW index)
```

Then:

```text
User Question
 ↓
Question embedding
 ↓
Vector similarity search (Cosine distance via pgvector)
 ↓
Relevant chunks
 ↓
Build prompt manually
 ↓
LLM API
 ↓
Answer
```

### Key Considerations
* **Async Ingestion**: Offload document chunking and embedding generation to `FastAPI BackgroundTasks` to prevent blocking the upload request.
* **Vector Indexing**: Use an `HNSW` index on the `document_chunks.embedding` column for fast approximate nearest neighbor (ANN) retrieval.

### Goal

Understand how RAG actually works instead of relying on a framework.

---

## Phase 4 — Manual Conversation Memory & Streaming

Add conversation history and real-time streaming manually.

### Implement

* Store conversations and conversation messages
* Load relevant conversation history
* Enforce context token budget (sliding window or message limits)
* Send history + retrieved context with the current request
* **Streaming Responses**: Stream LLM tokens to the client via Server-Sent Events (SSE)

### Flow

```text
User Message
 ↓
Load conversation history (token budgeted)
 ↓
Retrieve relevant documents
 ↓
Build context
 ↓
LLM (streaming mode)
 ↓
Stream tokens to client (SSE)
 ↓
Store completed response
```

### Goal

Understand the relationship between **tokens, context, history, RAG, and response streaming**.

---

## Phase 5 — Manual Tool Calling

Add tools without LangChain.

### Tools

```text
get_leave_balance()
check_calendar()
apply_leave()
```

Example:

```text
User
 ↓
LLM
 ↓
Decides tool is required
 ↓
Application executes tool
 ↓
Tool result
 ↓
LLM
 ↓
Final answer
```

### Goal

Understand how an LLM interacts with application functions.

---

## Phase 6 — Rebuild RAG with LangChain

Replace the manual RAG implementation with LangChain.

### Use

* Document loaders
* Text splitters
* Embeddings
* Vector store
* Retrievers
* Prompt templates
* Chains

### Goal

Understand:

```text
Manual implementation
        ↓
What LangChain abstracts
        ↓
LangChain implementation
```

Do not remove the manual implementation until this phase is complete.

---

## Phase 7 — LangChain Tools & Agent

Move tool calling to LangChain.

### Implement

```text
User Request
 ↓
LangChain Agent
 ↓
Choose tool
 ↓
Execute tool
 ↓
Read result
 ↓
Final response
```

### Goal

Understand LangChain's tool and agent abstractions.

---

## Phase 8 — Build the LangGraph Agent

Convert the leave assistant into a stateful workflow.

### Example

```text
User requests leave
        ↓
Understand request
        ↓
Retrieve leave policy
        ↓
Check leave balance
        ↓
Check calendar
        ↓
Is request valid?
    ↙           ↘
  No             Yes
  ↓               ↓
Explain        Request approval
                  ↓
             User approves
                  ↓
             Apply leave
                  ↓
              Confirm
```

### Implement

* Graph state
* Nodes
* Edges
* Conditional routing
* Tool calls
* Loops/retries
* Human approval
* Pause/resume
* Error handling

### Goal

Understand why LangGraph is useful for **stateful, multi-step agents**.

---

## Phase 9 — Testing & Production Basics

Add basic production practices.

### Backend

* Unit tests
* Integration tests
* API validation
* Authentication
* Authorization
* Logging
* Error handling
* Database transactions

### AI

* RAG retrieval testing
* Tool execution testing
* Agent workflow testing
* Failure/retry testing
* Prompt/version management

### Frontend

* API error handling
* Loading states
* Form validation
* Protected routes

### Goal

Turn the learning project into a small but properly structured application.
