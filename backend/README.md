# Backend

FastAPI backend that wraps the existing LangGraph-based assistant.

Run locally:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Endpoints:
- `POST /chat` - accepts JSON {"message","patient_id","thread_id"} and streams SSE chunks.
- `GET /patient/{patient_id}` - returns stored patient profile.
