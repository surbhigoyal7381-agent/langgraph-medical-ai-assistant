# Requirements for the LangGraph Medical AI Assistant

## 1. Purpose & Scope
- Deliver a conversational assistant for the Good Health Clinic that routes patient messages through a LangGraph workflow, uses GPT-based responses when an OpenAI key is supplied, and stores patient summaries for follow-up.
- Cover both the Python/LangGraph backend (state graph, memory updates, streaming API) and the Next.js frontend (chat UI, SSE consumption, profile polling).

## 2. Functional Requirements
1. **Patient messaging with decision routing.** Every incoming message enters a LangGraph state graph that routes to `handle_emergency` if the user text contains “emergency”, otherwise to `call_model`. This is implemented in `main.py:47-159` for the standalone script and `backend/engine.py:94-138` for the FastAPI engine, ensuring conversation control is centrally defined.
2. **LLM-powered replies augmented with patient history.** Model calls wrap the patient profile into `SystemMessage` prompts (`main.py:73-99`, `backend/engine.py:107-118`) so GPT can reference appointment history, allergies, medications, and follow-up needs whenever it generates responses.
3. **Persistent patient profile updates.** `write_memory` synthesizes a summary of the exchange (`backend/engine.py:120-138`) and stores it in either Redis (`backend/redis_store.py`) or the fallback `InMemoryStore`. This keeps patient records accessible from future threads while the frontend polls the stored profile (`frontend/components/PatientSidebar.js:6-26`).
4. **Emergency awareness.** The check node tags emergency exchanges (`backend/engine.py:94-98`), and the frontend highlights those responses with a clinical alert badge and red bubble background (`frontend/components/Chat.js:31-70`).
5. **Streaming SSE API.** `backend/app.py:43-54` exposes `POST /chat` that streams SSE chunks (`{"chunk": ..., "emergency": bool}`) so the chat UI can render partial LLM text (`frontend/components/Chat.js:21-58`).
6. **Patient/thread controls.** `frontend/pages/index.js:5-25` wires patient ID and thread ID inputs to both the chat widget and the sidebar so the same API can demonstrate per-patient memory and per-thread conversation tracking.

## 3. System Architecture & Data Flow
- **LangGraph flow:** `StateGraph` nodes (`check_condition`, `call_model`, `handle_emergency`, `write_memory`) are compiled once per engine instance and run with `MemorySaver` for the in-flight exchange plus `RedisStore`/`InMemoryStore` for long-term state (`backend/engine.py:57-92, 120-138`).
- **Model layer:** `ChatOpenAI` is instantiated when `OPENAI_API_KEY` exists; otherwise `MockModel` echoes the last human prompt for offline testing (`backend/engine.py:32-90`). All `SystemMessage` prompts embed the clinic name and patient history to ground responses (`backend/engine.py:41-118`).
- **Frontend flow:** The `Chat` component sends `POST /chat`, interprets SSE frames, patches the last AI message as chunks arrive, and flags emergency exchanges (`frontend/components/Chat.js:9-58`). The sidebar hits `GET /patient/{id}` every two seconds to stay in sync with the backend memory store (`frontend/components/PatientSidebar.js:6-26`).
- **API surface:** FastAPI exposes `/health`, `/patient/{patient_id}`, and `/chat` inside `backend/app.py:32-54`, with CORS preflight support for the Next.js origin (`backend/app.py:15-21`).

## 4. Non-functional & Operational Requirements
- **Dependencies:** Python 3.11 (backend Dockerfile), Node 18 (frontend Dockerfile). Backend packages are listed in `requirements.txt` and `backend/requirements.txt`; frontend packages live in `frontend/package.json`.
- **Persistence & scaling:** Redis usage is optional; set `REDIS_URL` to `redis://redis:6379/0` when running Docker Compose to swap `InMemoryStore` for `RedisStore` (`backend/engine.py:81-93`) and persist patient profiles between restarts.
- **Security considerations:** `OPENAI_API_KEY` must remain secret. The repo currently lacks authentication, so TLS/identity gating should be added before production use.
- **Observability:** SSE streaming means the API should be monitored for partial message backpressure; backend logs (via Uvicorn) and frontend console output are primary diagnostics.

## 5. Run & Deployment Steps
1. **Establish environment variables.** Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (required for real GPT responses). Optionally set `REDIS_URL=redis://localhost:6379/0` when running alongside Redis. Without `OPENAI_API_KEY`, the engine uses `MockModel` (`backend/engine.py:34-45`) so the stack remains runnable.
2. **Backend setup.**
   - `cd backend`
   - `python -m venv .venv` && `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Unix)
   - `pip install --upgrade pip`
   - `pip install -r requirements.txt`
   - `uvicorn app:app --host 0.0.0.0 --port 8000`
   (See `backend/README.md` for the same sequence.)
3. **Frontend setup.**
   - `cd frontend`
   - `npm install`
   - `npm run dev` (serves Next.js at `http://localhost:3000`)
   - Ensure the backend is reachable at `http://localhost:8000`.
4. **Full stack via Docker Compose (recommended for repeatability).**
   - From repo root: `docker compose up -d --build`
   - This brings up Redis, FastAPI backend, and Next.js frontend on ports `6379`, `8000`, and `3000`.
   - Backend automatically receives `OPENAI_API_KEY` and `REDIS_URL` from environment (`docker-compose.yml`).
5. **Validation.**
   - `curl http://localhost:8000/health`
   - `curl http://localhost:8000/patient/1`
   - Trigger chat: `curl -N -H "Content-Type: application/json" -d '{"message":"hello","patient_id":"1","thread_id":"1"}' http://localhost:8000/chat`
   - Confirm frontend renders streaming bubbles and that `/patient/1` documents update immediately after a chat exchange.

## 6. Monitoring & Future Work
- **Limitations:** `MockModel` is a placeholder; replace with GPT-4+ or another medically tuned model for production. Currently, `write_memory` writes plain text summaries; for structured records, consider keyed fields or vector embeddings.
- **Next milestones:** Harden error handling (timeouts/retries for LLM calls), add auth (API tokens or OAuth), capture structured patient metadata, and optionally persist graphs or conversation IDs for audit trails.
