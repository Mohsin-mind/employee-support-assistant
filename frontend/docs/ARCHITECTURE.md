# Frontend Architecture & Design Rules

This document defines the architectural standard, directory layout, state management strategy, and component boundaries for the **Employee Support Assistant** frontend.

---

## 1. Directory Structure

```text
frontend/
├── src/
│   ├── main.tsx                    # Application entry point
│   ├── App.tsx                     # Providers (QueryClientProvider, Router)
│   ├── index.css                   # Core design tokens, global themes & utility classes
│   │
│   ├── api/                        # HTTP client & domain API fetchers
│   │   ├── client.ts               # Configured Axios instance with interceptors
│   │   ├── health.api.ts           # System health check API
│   │   ├── chat.api.ts             # Chat session, message sending, SSE reader
│   │   ├── documents.api.ts        # Document upload and listing APIs
│   │   └── leave.api.ts            # Leave balance and application APIs
│   │
│   ├── components/                 # Reusable UI components
│   │   ├── common/                 # Primitives: Button, Input, Modal, Loader, Card
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Loader.tsx
│   │   ├── chat/                   # Chat window, message bubbles, streaming cursor
│   │   ├── documents/              # Document uploader, chunk previewer, doc list
│   │   └── leave/                  # Leave balance card, leave request form, status pill
│   │
│   ├── pages/                      # Page-level route views
│   │   ├── HomePage.tsx            # System overview, health metrics, phase roadmap
│   │   ├── ChatPage.tsx            # Interactive AI assistant chat page
│   │   ├── DocumentsPage.tsx       # Document knowledge base management page
│   │   └── LeavePage.tsx           # Employee leave self-service page
│   │
│   ├── hooks/                      # Custom React / TanStack Query hooks
│   │   ├── useHealth.ts            # Hook for health polling
│   │   ├── useChat.ts              # Hook for sending messages & SSE streaming
│   │   ├── useDocuments.ts         # Hook for querying & uploading documents
│   │   └── useLeave.ts             # Hook for querying balance & submitting leave
│   │
│   ├── schemas/                    # Client-side validation schemas (Zod)
│   │   ├── chat.schema.ts          # Validates chat input length & metadata
│   │   ├── document.schema.ts      # Validates file types and upload limits
│   │   └── leave.schema.ts         # Matches backend Pydantic LeaveRequestCreate
│   │
│   ├── types/                      # TypeScript domain models & interfaces
│   │   ├── health.ts               # HealthResponse, HealthData
│   │   ├── chat.ts                 # Conversation, Message, StreamToken
│   │   ├── document.ts             # Document, DocumentChunk
│   │   └── leave.ts                # LeaveBalance, LeaveRequest
│   │
│   ├── constants/                  # Application constants, route paths, storage keys
│   │   └── constants.ts
│   │
│   ├── utils/                      # Helper utilities (date formatters, token counters)
│   │   └── helpers.ts
│   │
│   └── config/                     # Environment configuration
│       └── env.ts
│
├── .env                            # Client environment variables
├── package.json
├── tsconfig.json
└── vite.config.ts                  # Vite config with dev server proxy to /api
```

---

## 2. Technology Stack & Responsibilities

| Purpose | Technology | Standard Usage |
| :--- | :--- | :--- |
| **Build & Tooling** | Vite + TypeScript | Strict typing with `tsc -b` validation |
| **Server State** | TanStack Query (`@tanstack/react-query`) | Query caching, polling, optimistic updates, mutation states |
| **Form Handling** | React Hook Form | Uncontrolled performant form inputs |
| **Form Validation** | Zod + `@hookform/resolvers` | Client-side validation mirroring backend Pydantic rules |
| **HTTP Client** | Axios | Custom instance in `api/client.ts` with error normalization |
| **Routing** | React Router v6 | Declarative route hierarchy |
| **UI State** | React `useState` / `useReducer` | Local component state; Zustand only if cross-cutting global state is needed |
| **Styling** | Tailwind CSS v4 + `@tailwindcss/vite` | Modern utility classes, CSS `@theme`, dark cyber-glass styling, Inter font |

---

## 3. Symmetric Validation (Zod ↔ Pydantic)

Frontend validation schemas MUST match backend Pydantic constraints:

```typescript
// frontend/src/schemas/leave.schema.ts
import { z } from 'zod';

export const LeaveRequestSchema = z.object({
  employee_id: z.number().int().positive(),
  days: z.number().int().min(1).max(30),
  reason: z.string().min(3).max(500),
});

export type LeaveRequestInput = z.infer<typeof LeaveRequestSchema>;
```

Matches backend:
```python
# backend/app/schemas/leave.py
class LeaveRequestCreate(BaseModel):
    employee_id: int = Field(gt=0)
    days: int = Field(gt=0, le=30)
    reason: str = Field(min_length=3, max_length=500)
```

---

## 4. Architectural Invariants (Do Not Violate)

1. **No Direct Axios Calls in Components**: Components must call custom hooks (`hooks/`) or domain API functions (`api/`), never raw `axios.get` or `axios.post`.
2. **Domain Parity**: Maintain strict alignment across `api/`, `components/`, `hooks/`, `schemas/`, and `types/` for each domain (`chat`, `documents`, `leave`).
3. **Tailwind CSS v4 Design Standard**: Style using Tailwind CSS v4 utility classes and CSS theme tokens in `index.css`. Maintain design consistency (dark theme, slate palette, indigo/cyan/emerald accents, rounded cards).
