# Repository Rules & Coding Standards

This document establishes the mandatory architectural rules, coding standards, and common patterns for the **Employee Support Assistant** project. All developers and AI pair-programming agents must strictly adhere to these practices to ensure consistency, eliminate code drift, and maintain high code quality.

---

## 1. Architecture Links & Core Documents

Before writing or modifying code, consult the primary architecture documents:

- **[Global Architecture Overview](docs/ARCHITECTURE.md)**: End-to-end request flow from React to FastAPI, PostgreSQL, and the AI subsystem.
- **[Backend Architecture Specification](backend/docs/ARCHITECTURE.md)**: Detailed backend directory layout, layer boundaries, and database tables.
- **[Frontend Architecture Specification](frontend/docs/ARCHITECTURE.md)**: State management (TanStack Query), component boundaries, and Zod validation.
- **[Development Phases & Roadmap](DEVELOPMENT_PHASES.md)**: 9-phase progressive guide from scaffolding to LangGraph.

---

## 2. Universal Code Patterns & Best Practices

### A. Constants & Enums — No Static Magic Strings
1. **Central Definition**: All system strings, roles, statuses, document states, error codes, and standard messages MUST be defined in `backend/app/core/constants.py`.
2. **No Raw String Literals**:
   - ❌ **Forbidden**: `if status == "pending":`, `role = "assistant"`, `raise Exception("Not found")`
   - ✅ **Mandatory**: `if status == LeaveStatus.PENDING:`, `role = MessageRole.ASSISTANT`, `Messages.NOT_FOUND`
3. **Use Enum Classes**:
   - Use `StrEnum` for categorical values (`LeaveStatus`, `LeaveType`, `MessageRole`, `DocumentStatus`, `ErrorCode`).
   - Use `Messages` class for standard user-facing notices (`Messages.SUCCESS`, `Messages.CREATED`, `Messages.DELETED`).

---

### B. Common Reusable Helpers (`core/helpers.py`)
1. **Single Source of Truth**: Any calculation, formatting, or data transformation performed in more than one place MUST live as a reusable helper in `backend/app/core/helpers.py`.
2. **Never Duplicate Utility Logic**:
   - Time & Timezone: Always use `utc_now()` (timezone-aware UTC).
   - Identifiers: Use `generate_uuid()`.
   - Date Math: Use `calculate_business_days(start, end)` instead of ad-hoc loops.
   - Text Formatting: Use `truncate_text(str, max_len)`.
   - Batch Processing: Use `chunk_list(items, size)`.

---

### C. Consistent Response Pattern (`schemas/common.py`)
1. **Uniform Envelope**: Every API endpoint must return a structured JSON response wrapped in `APIResponse[T]` or `PaginatedResponse[T]`. Never return raw dictionaries or naked arrays.
2. **Response Factories**:
   ```python
   # For single object or action result:
   return success_response(data=employee, message=Messages.CREATED)

   # For list of items with pagination:
   return paginated_response(
       items=employees,
       total_items=total_count,
       page=params.page,
       page_size=params.page_size
   )
   ```
3. **Standard Response Structure**:
   ```json
   {
     "success": true,
     "message": "Operation completed successfully.",
     "data": { ... }
   }
   ```

---

### D. Consistent Error Handling & Exception Raisers (`exceptions/`)
1. **Structured Exception Hierarchy**: All business and operational exceptions inherit from `AppException(message, status_code, error_code, details)`.
2. **Never Return Raw Error Dicts from Routes**: When a validation or business rule fails, raise domain exceptions using factory helpers:
   ```python
   from backend.app.exceptions.exceptions import raise_not_found, raise_bad_request, raise_conflict

   # Raising standard errors:
   raise_not_found("Employee", employee_id)
   raise_bad_request("Leave start date cannot be after end date")
   raise_conflict("A leave request already exists for these dates")
   ```
3. **Automatic Normalization**: FastAPI exception handlers in `backend/app/exceptions/handlers.py` automatically catch `AppException`, `RequestValidationError`, and `SQLAlchemyError` and format them into:
   ```json
   {
     "success": false,
     "error": {
       "code": "NOT_FOUND",
       "message": "Employee with identifier '42' was not found.",
       "details": { "entity": "Employee", "identifier": "42" }
     }
   }
   ```

---

### E. Validation Pattern (Pydantic v2 & Zod)
1. **Backend (Pydantic v2)**:
   - Strict typing with `BaseModel` for all inputs and outputs in `backend/app/schemas/`.
   - Enforce constraints with `Field(gt=..., le=..., min_length=..., max_length=...)`.
   - Separate schemas: `[Entity]Create`, `[Entity]Update`, `[Entity]Response`, `[Entity]Filter`.
2. **Frontend (Zod)**:
   - Client schemas in `frontend/src/schemas/` must symmetrically mirror backend Pydantic constraints (e.g. min lengths, numeric limits).

---

### F. Layered Architecture Invariants
```text
Route (HTTP / Schemas) 
  → Service (Business Logic & Coordination) 
    → Repository (SQLAlchemy Queries) 
      → ORM Model (PostgreSQL)
```

1. **Routes (`api/routes/`)**:
   - Thin handlers only.
   - Inject dependencies (`get_db`, `current_user`).
   - Validate input with Pydantic schemas.
   - Delegate immediately to the service layer.
   - **Never** execute database queries or SQL expressions in routes.
2. **Services (`services/`)**:
   - Pure business logic.
   - Coordinate multiple repositories, external APIs, and AI layers.
   - Throw domain exceptions (`raise_not_found`, `raise_bad_request`).
3. **Repositories (`repositories/`)**:
   - Encapsulate all database operations using SQLAlchemy 2.0 `select()`, `insert()`, `update()`.
   - Only place where SQLAlchemy queries are constructed.
4. **Models (`db/models/`)**:
   - Pure SQLAlchemy 2.0 Declarative models using `Mapped[...]` and `mapped_column(...)`.
   - Inherit from `Base` and include `TimestampMixin` for audit timestamps.
5. **AI Subsystem (`ai/`)**:
   - Isolated in `backend/app/ai/`.
   - Never couple web framework code or HTTP concepts into AI tools or chains.

---

### G. Python Style & Quality Rules
- **Type Annotations**: Mandatory on all function signatures and return types.
- **Async/Await**: All database access and network calls must be asynchronous.
- **Logging**: Use structured logger from `backend/app/core/logging.py`, never raw `print()` statements in production code.

---

## 3. Frontend TypeScript & React Coding Standards

### A. Constants & Enums (`frontend/src/constants/constants.ts`)
1. **Mirror Backend Enums**: Categorical values (`LeaveStatus`, `LeaveType`, `MessageRole`, `DocumentStatus`, `ErrorCode`) must be imported from `src/constants/constants.ts`.
2. **No Magic Strings or Routes**:
   - ❌ **Forbidden**: `navigate("/leave")`, `status === "approved"`, `role === "user"`
   - ✅ **Mandatory**: `navigate(ROUTES.LEAVE)`, `status === LeaveStatus.APPROVED`, `role === MessageRole.USER`
3. **Standard Notices**: Use `UI_MESSAGES` for standard user-facing error and success strings.

---

### B. Common Reusable Helpers (`frontend/src/utils/helpers.ts`)
1. **Central Formatting**: All transformations used in more than one component must live in `src/utils/helpers.ts`.
2. **Standard Utilities**:
   - Date & Time: `formatDate(date)`, `formatDateTime(date)`
   - Error Extraction: `getErrorMessage(error)`
   - Text Truncation: `truncateText(str, maxLen)`
   - File Size: `formatFileSize(bytes)`
   - Styling: `classNames(...)`

---

### C. Standard Response & Error Types (`frontend/src/types/common.ts`)
1. **Symmetric API Types**: Consume responses via `APIResponse<T>`, `PaginatedResponse<T>`, and `PageMeta`.
2. **Normalized Errors**: Interceptors in `api/client.ts` format all HTTP failures into `AppError { message, code, status, details }`.

---

### D. Data Fetching & Server State (`hooks/`)
1. **TanStack Query Only**: Never trigger raw `axios` calls directly inside React components or `useEffect`.
2. **Encapsulate in Custom Hooks**:
   ```typescript
   // hooks/useLeave.ts
   export const useLeaveBalance = () => {
     return useQuery({
       queryKey: ['leave-balance'],
       queryFn: fetchLeaveBalance,
     });
   };
   ```
3. **Mutations**: Always invalidate matching query keys upon successful mutations to guarantee fresh UI state.

---

### E. Form & Validation Pattern (React Hook Form + Zod)
1. **Zod Validation**: Forms must be validated using Zod schemas (`src/schemas/`) with `@hookform/resolvers/zod`.
2. **Constraint Symmetry**: Ensure Zod constraints (min/max string lengths, numeric ranges) symmetrically mirror backend Pydantic models.
3. **Form Component**: Use reusable `Input` and `Button` primitives from `components/common/`.

---

### F. Component Layering Invariants
```text
Page (Route View) 
  → Domain Components (chat/, documents/, leave/) 
    → Common UI Primitives (Button, Input, Modal, Loader)
```
4. **Tailwind CSS v4 Styling Standards**:
   - **Framework Standard**: The project strictly uses **Tailwind CSS v4** via the `@tailwindcss/vite` plugin.
   - **Tailwind v4 vs v3 (Rules to Remember)**:
     - ❌ **No `tailwind.config.js` or `postcss.config.js`**: In v4, configuration is CSS-first. Never generate or expect a JavaScript configuration file.
     - ❌ **No `@tailwind base/components/utilities;`**: Replaced by a single `@import "tailwindcss";` in `src/index.css`.
     - ✅ **`@theme` Directive**: Custom colors, fonts, and breakpoints are declared in the CSS `@theme { ... }` block.
     - ✅ **Native CSS Variables**: All `@theme` properties generate native CSS variables (`--color-brand-indigo`) automatically available in utility classes.
     - ✅ **Zero-Config Content**: Template scanning is automatic; no manual `content` array glob configuration.
   - **Color & Opacity Best Practice (HEX vs Alpha)**:
     - Define theme base colors using clean **6-digit HEX** in `@theme` (e.g. `--color-slate-950: #0f1422`).
     - **Do NOT** hardcode opaque colors where glassmorphism is needed: backdrop blur (`backdrop-blur-md`) requires translucency.
     - Always use Tailwind's **opacity modifier syntax** with base colors for translucent glass effects: `bg-slate-900/70`, `border-white/10`, `shadow-indigo-500/20`.
     - *Note on Color Quality*: 8-digit HEX (`#121826b3`) and `rgba(18, 24, 38, 0.7)` have identical 32-bit color rendering quality, but Tailwind's `/opacity` modifier syntax is preferred for consistency and maintainability.
   - **Utility Class Ordering**:
     1. Layout/Display (`flex`, `grid`, `hidden`)
     2. Position & Sizing (`relative`, `w-full`, `max-w-md`, `h-12`)
     3. Spacing (`p-4`, `mx-auto`, `gap-3`)
     4. Typography (`text-sm`, `font-semibold`, `tracking-wide`)
     5. Background & Borders (`bg-slate-900/80`, `border`, `border-white/10`, `rounded-xl`)
     6. Effects & Interactivity (`shadow-lg`, `hover:-translate-y-0.5`, `transition-all`)
