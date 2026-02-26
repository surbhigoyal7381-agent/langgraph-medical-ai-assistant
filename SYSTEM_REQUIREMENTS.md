# Systems Requirements Document

**Project:** LangGraph Medical AI Assistant — Good Health Clinic

**Repository root:** See project files at repository root. Key folders:
- `backend/` — FastAPI app and LangGraph engine (`backend/app.py`, `backend/engine.py`, `backend/redis_store.py`, `backend/requirements.txt`, `backend/Dockerfile`).
- `frontend/` — Next.js + Tailwind UI (production-ready Dockerfile and Next.js pages/components).
- `docker-compose.yml` — development/production compose manifest (starts `backend`, `frontend`, and optional `redis`).
- `.env.example` — environment variable examples.

**Date:** 2026-02-26 (updated)

## Purpose & Scope
- Purpose: Describe system-level runtime, deployment, and operational requirements for the full-stack conversational assistant (FastAPI backend + Next.js frontend) built on top of a LangGraph flow.
- Scope: Local development, containerized deployment (Docker Compose), and short notes for production hardening.

## High-level Architecture
- Input/API: `POST /chat` (SSE streaming) and `GET /patient/{patient_id}` exposed by FastAPI in `backend/app.py`.
- Control: `backend/engine.py` wraps the LangGraph `StateGraph` with nodes: `check_condition`, `call_model`, `handle_emergency`, `write_memory`.
- Model: `ChatOpenAI` (via `langchain_openai`) when `OPENAI_API_KEY` is configured; `MockModel` fallback when the key is absent to allow offline testing.
- Persistence: optional Redis-backed `RedisStore` (`backend/redis_store.py`) used when `REDIS_URL` is set. Defaults to `InMemoryStore` and `MemorySaver` for ephemeral operation.
- Frontend: Next.js app (`frontend/`) that connects to backend SSE `/chat`, renders streaming AI text, and polls `GET /patient/{id}` for the persistent profile (Patient Sidebar).

## Key Functional Requirements
- Streaming chat responses via SSE from `POST /chat` with JSON payloads: `{ "chunk": "...", "emergency": true|false }`.
- Emergency routing: messages containing the word `"emergency"` take the emergency path (`handle_emergency`) and the frontend highlights such responses with a clinical badge and red styling.
- Persistent patient profile: `write_memory` writes summary text under namespace `("patient_interactions", patient_id)` and key `patient_data_memory`. When `REDIS_URL` is configured, data persists across restarts.
- Frontend session control: header inputs allow switching `patient_id` and `thread_id` to demonstrate per-patient persistence and per-thread state.

## Non-functional Requirements
- Python runtime: 3.11 recommended (the backend Dockerfile uses `python:3.11-slim`).
- Node runtime: Node 18 (the frontend Dockerfile uses `node:18`).
- Ports: backend listens on `8000` (uvicorn), frontend on `3000` (Next.js). Docker Compose maps these to host ports.
- Performance: model calls go to OpenAI; scale and latency depend on model/region. Use caching and batching for high throughput.

## Dependencies
- Backend (`backend/requirements.txt`) highlights: `fastapi`, `uvicorn[standard]`, `python-dotenv`, `langchain`, `langgraph`, `langchain-openai`, `redis`.
- Frontend (`frontend/package.json`) highlights: `next` (13+), `react`, `react-dom`, `tailwindcss` (pinned to 3.4.8 in builds), `lucide-react`, `react-markdown`, `remark-gfm`, `swr` or similar for client data fetching.

## Environment Variables
- `OPENAI_API_KEY` — required for real LLM access. If not set, the `MockModel` runs locally.
- `REDIS_URL` — optional. Set to `redis://redis:6379/0` when running with the bundled `redis` service in `docker-compose.yml` to enable durable persistence.
- `FRONTEND_PORT` / `BACKEND_PORT` — optional overrides used in container orchestration.

## Run & Deployment Instructions
Local development (Python backend + Next.js frontend):

1) Backend virtualenv & run (dev):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
# Run with uvicorn (serve on 0.0.0.0:8000)
uvicorn app:app --host 0.0.0.0 --port 8000
```

2) Frontend development:

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

3) Full stack with Docker Compose (recommended for repeatable local tests):

```powershell
# from repository root
docker compose up -d --build
# tail backend logs
docker compose logs -f backend
# open frontend
start http://localhost:3000
```

Notes:
- `docker-compose.yml` includes a `redis` service and the `backend` is configured to use `REDIS_URL=redis://redis:6379/0` in compose when present.
- The backend container runs `uvicorn app:app --host 0.0.0.0 --port 8000` and the frontend container runs a Next.js production server.

## API Endpoints
- `GET /health` — basic health check.
- `GET /patient/{patient_id}` — returns JSON with the stored patient profile (pulled from configured store).
- `POST /chat` — streaming endpoint (SSE). Request body JSON: `{ "message": "...", "patient_id": "1", "thread_id": "1" }`.

Example SSE test using curl (streams events):

```bash
curl -N -H "Accept: text/event-stream" -H "Content-Type: application/json" \
  -d '{"message":"hello","patient_id":"1","thread_id":"1"}' \
  http://localhost:8000/chat
```

Quick health and patient checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/patient/1
```

## Observability & Troubleshooting
- Logs: `docker compose logs -f backend` shows uvicorn and runtime logs.
- Common issue: relative imports inside `backend` can cause `ImportError` when running `uvicorn app:app` from the container root. This has been fixed by using top-level imports (`engine`, `redis_store`) and packaging the `backend` files at container `/app` root.
- If Redis is configured but unreachable, the backend falls back to `InMemoryStore` but logs connectivity errors.

## Security & Privacy
- Keep `OPENAI_API_KEY` out of source control; prefer environment secrets or secret stores (Vault, cloud provider secrets) for production.
- If storing real PHI, enable encryption at rest, access auditing, and follow regional healthcare compliance (HIPAA, GDPR).
- Add HTTPS/TLS in front of both backend and frontend for production.

## Testing & Validation
- Smoke test (local): after `docker compose up -d --build`, open `http://localhost:3000`, send a message, and confirm streaming bubbles appear and that `GET /patient/{id}` shows updates after the exchange.
- Unit tests: add tests for `check_condition`, model invocation paths, and `RedisStore` serialization/deserialization.

## Known Limitations
- Offline fallback: `MockModel` provides simple echoed responses; not suitable for production accuracy testing.
- The `write_memory` step writes free-text summaries; consider structured schemas for production use.
- No authentication/authz implemented on the API — add an API gateway or token-based auth for production.

## Recommended Next Steps
- Add CI to run linting, tests, and build images in CI.
- Add structured storage for patient records and migration scripts.
- Harden LLM error handling, timeouts, and retries; add request-size limits.
- Add HTTPS, authentication, and RBAC for clinical operations.

---
*Document updated to reflect backend FastAPI, SSE streaming, Redis-backed persistence option, Next.js frontend, Docker Compose usage, and import-fix notes (2026-02-26).* 
