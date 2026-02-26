import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

from engine import LangGraphEngine

app = FastAPI(title="LangGraph Medical Assistant API")

app.add_middleware(
    CORSMiddleware,
    # During local development allow common localhost ports; allow '*' if you
    # prefer to accept requests from any origin. Narrow this for production.
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
