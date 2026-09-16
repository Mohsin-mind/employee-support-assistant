# Python & System Coding Standards

These rules are automatically loaded into the AI agent context for the **Employee Support Assistant** repository.

## 1. Core Architecture References
- **Global Overview**: [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
- **Backend Architecture**: [backend/docs/ARCHITECTURE.md](../../backend/docs/ARCHITECTURE.md)
- **Frontend Architecture**: [frontend/docs/ARCHITECTURE.md](../../frontend/docs/ARCHITECTURE.md)
- **Roadmap & Phases**: [DEVELOPMENT_PHASES.md](../../DEVELOPMENT_PHASES.md)
- **Root Rules**: [AGENTS.md](../../AGENTS.md)

---

## 2. Mandatory Python Implementation Patterns

### Constants First (`backend/app/core/constants.py`)
- Do not use magic strings or numbers anywhere in business logic.
- All statuses (`LeaveStatus`), roles (`MessageRole`), error codes (`ErrorCode`), document states (`DocumentStatus`), pagination limits, and standard messages (`Messages`) MUST be imported from `backend.app.core.constants`.

### Reusable Utilities (`backend/app/core/helpers.py`)
- Any repetitive calculation, string mutation, date logic, or list batching MUST be placed in `backend.app.core.helpers`.
- Use `utc_now()` for all timestamps.
- Use `generate_uuid()` for UUID identifiers.
- Use `calculate_business_days(start, end)` for leave date spans.
- Use `truncate_text(text, max_length)` for previews.

### Standard Response Envelope (`backend/app/schemas/common.py`)
- Endpoints must always return `success_response(data=..., message=...)` or `paginated_response(items=..., total_items=..., page=..., page_size=...)`.
- Direct un-enveloped dictionaries or lists are forbidden.

### Standard Exception Throwers (`backend/app/exceptions/exceptions.py`)
- Do not return manual error JSON objects.
- Raise typed exceptions via raiser helpers:
  - `raise_not_found(entity_name, identifier)`
  - `raise_bad_request(message, details=None)`
  - `raise_conflict(message, details=None)`
- Handlers in `backend/app/exceptions/handlers.py` will catch and format them automatically.

### Layer Separation
- **Routes (`api/routes/`)**: Validate request → Call service → Return response.
- **Services (`services/`)**: Orchestrate business logic, call AI subsystem, throw domain exceptions.
- **Repositories (`repositories/`)**: Construct and execute SQLAlchemy 2.0 async queries.
- **Models (`db/models/`)**: Declarative SQLAlchemy models with `Mapped` type hints.

---

## 3. Mandatory Frontend Implementation Patterns

### Constants & Navigation (`frontend/src/constants/constants.ts`)
- Mirror backend enums (`LeaveStatus`, `LeaveType`, `MessageRole`, `DocumentStatus`, `ErrorCode`).
- Use `ROUTES` for navigation paths.
- Use `UI_MESSAGES` for user-facing notices.

### Reusable Utilities (`frontend/src/utils/helpers.ts`)
- Date formatting: `formatDate()`, `formatDateTime()`.
- Error parsing: `getErrorMessage(error)`.
- Helpers: `truncateText()`, `formatFileSize()`, `classNames()`.

### API & Data Fetching
- Consume responses via `APIResponse<T>` and `PaginatedResponse<T>` (`types/common.ts`).
- Encapsulate server state in TanStack Query hooks (`hooks/`).
- Never perform raw axios calls directly inside React components.

### Form Validation
- Validate forms with Zod schemas in `schemas/` matching backend Pydantic models.
- Use React Hook Form with `@hookform/resolvers/zod`.

### Component Layering & Styling
- **Pages (`pages/`)** → **Domain Components (`components/{chat,documents,leave}/`)** → **Primitives (`components/common/`)**.
- Use **Tailwind CSS v4** (`@tailwindcss/vite`) exclusively:
  - Do NOT create `tailwind.config.js` or `postcss.config.js` (v4 uses CSS-first `@theme`).
  - Configure theme tokens directly inside `src/index.css` under `@theme`.
  - Base theme colors should use standard **6-digit HEX** (`#0f1422`, `#6366f1`).
  - For translucent/glassmorphism styling, always use Tailwind's **opacity modifier syntax** (e.g. `bg-slate-900/70`, `border-white/10`, `shadow-indigo-500/20`) rather than arbitrary inline rgba expressions.

