import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

from engine import LangGraphEngine
from config import settings

app = FastAPI(title="LangGraph Medical Assistant API")

# Hardened CORS configuration driven by environment variables.
# - In development (ENV != 'production') we allow localhost origins for convenience.
# - In production, set ALLOWED_ORIGINS to a comma-separated list of allowed origins.
if settings.ENV == 'production':
    # ensure safe configuration
    settings.require_production_safe()
    allow_origins = settings.ALLOWED_ORIGINS
else:
    # allow common local dev hosts; keep explicit list rather than '*'
    allow_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3001',
        'http://localhost:3004',
        'http://127.0.0.1:3004',
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Length"],
)

engine = LangGraphEngine()


class ChatRequest(BaseModel):
    message: str
    patient_id: str = "1"
    thread_id: str = "1"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/patient/{patient_id}")
def get_patient(patient_id: str):
    profile = engine.get_patient_profile(patient_id)
    return JSONResponse({"patient_id": patient_id, "profile": profile})


@app.post("/chat")
async def chat(req: ChatRequest):
    # StreamingResponse with generator that yields SSE-style chunks
    async def event_stream():
        # Wrap user message as list
        user_messages = [{"role": "human", "content": req.message}]
        try:
            for chunk in engine.stream_chat(user_messages, patient_id=req.patient_id, thread_id=req.thread_id):
                # chunk is a dict like {"chunk": text, "emergency": bool}
                data = json.dumps(chunk)
                yield f"data: {data}\n\n"
        except Exception as e:
            # Log full traceback to server stdout so we can inspect backend errors
            import traceback
            traceback.print_exc()
            # Send an SSE error message to the client before closing
            err_payload = json.dumps({"error": str(e)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
