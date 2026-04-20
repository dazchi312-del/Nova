# nova.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import your existing Phase 10 engine
from core.loop import run_turn, breaker
from core.memory import init_db, new_session, close_session

app = FastAPI(title="Project Nova API", version="0.11.0")

# --- Schemas ---
class ChatRequest(BaseModel):
    session_id: str
    message: str
    dry_run: bool = False

class ChatResponse(BaseModel):
    response: str
    score: float

class SessionResponse(BaseModel):
    session_id: str

# --- Startup ---
@app.on_event("startup")
def startup_event():
    init_db()
    print("\n[System] Nova Headless Engine Online.")
    print("[System] Listening on http://127.0.0.1:8000\n")

# --- Endpoints ---
@app.get("/session/new", response_model=SessionResponse)
def create_session():
    """Generates a new SQLite memory session"""
    sid = new_session()
    return {"session_id": sid}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """Passes the prompt through the RAG and Hardware Breaker"""
    try:
        response, score = run_turn(req.session_id, req.message, dry_run=req.dry_run)
        return {"response": response, "score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telemetry")
def telemetry_endpoint():
    """Pings the RTX 5090 hardware sensor"""
    is_safe, msg = breaker.check_pressure()
    return {
        "hardware_safe": is_safe,
        "status": msg
    }

if __name__ == "__main__":
    # Boot the server using Uvicorn
    uvicorn.run("nova:app", host="127.0.0.1", port=8000, log_level="warning")