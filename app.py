"""
Maternal AI Assistant — FastAPI Server
Stripped to: /chat, /health, /sensor-context
"""

import os
import uuid
import re
import ast
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import uvicorn
from config import Config
from agents.agent_decision import process_query

config = Config()
app = FastAPI(title="Maternal AI Assistant", version="1.0")

# Static files
os.makedirs("./data/qdrant_db", exist_ok=True)
os.makedirs("./data/docs_db", exist_ok=True)
os.makedirs("./data/parsed_docs", exist_ok=True)

try:
    app.mount("/data", StaticFiles(directory="data"), name="data")
except Exception:
    pass

templates = Jinja2Templates(directory="templates")


class ChatRequest(BaseModel):
    query: str
    mother_id: str = "maternal_main"
    language: str = "en"


class SensorContextResponse(BaseModel):
    mother_id: str
    status: str
    message: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Maternal AI Assistant"}


def extract_text_from_content(content) -> str:
    """Extract clean string text regardless of nested dicts, lists, or stringified structures."""
    if not content:
        return ""

    # If content is a list of blocks/dicts
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
            elif isinstance(block, str):
                text_parts.append(block)
        return "".join(text_parts)

    # Convert to string for inspection
    text_str = str(content)

    # Check if stringified list like "[{'type': 'text', 'text': '...'}]"
    if text_str.startswith("[{") or "'text':" in text_str or '"text":' in text_str:
        try:
            parsed = ast.literal_eval(text_str)
            if isinstance(parsed, list):
                return "".join(
                    item.get("text", "") for item in parsed if isinstance(item, dict)
                )
        except Exception:
            pass

        # Regex fallback to extract text value directly inside quotes
        match = re.search(r"['\"]text['\"]\s*:\s*['\"](.*?)['\"](?:\s*\}|\s*,)", text_str, re.DOTALL)
        if match:
            return match.group(1).replace("\\n", "\n").replace("\\'", "'")

    return text_str


@app.post("/chat")
def chat(request: ChatRequest):
    """Main chat endpoint — routes to CONVERSATION or RAG agent."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Future: pull sensor context from SQLite here
        sensor_context = _get_sensor_context_str(request.mother_id)

        result = process_query(
            query=request.query,
            mother_id=request.mother_id,
            sensor_context=sensor_context
        )

        # Extract last AI message
        messages = result.get("messages", [])
        response_text = ""
        for msg in reversed(messages):
            from langchain_core.messages import AIMessage
            if isinstance(msg, AIMessage) and msg.content:
                response_text = extract_text_from_content(msg.content)
                break

        if not response_text:
            response_text = "I'm here to help with your pregnancy questions. What would you like to know?"

        return {
            "status": "success",
            "response": response_text,
            "agent": result.get("agent_name", "CONVERSATION_AGENT"),
            "mother_id": request.mother_id
        }

    except Exception as e:
        print(f"[/chat] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensor-context/{mother_id}")
def get_sensor_context(mother_id: str):
    """Pull latest sensor data for a mother — reads from SQLite written by Pi."""
    db_path = config.sensor.sqlite_path
    
    if not os.path.exists(db_path):
        return {
            "mother_id": mother_id,
            "status": "no_data",
            "message": "No sensor data available. Waiting for Raspberry Pi connection.",
            "vitals": None,
            "active_flags": [],
            "trend": None
        }

    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        # Latest vitals
        vitals_row = conn.execute("""
            SELECT * FROM vitals 
            WHERE mother_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (mother_id,)).fetchone()

        # Active flags
        flags = conn.execute("""
            SELECT flag_name, severity, reasoning, timestamp 
            FROM fusion_flags 
            WHERE mother_id = ? AND is_active = 1
            ORDER BY timestamp DESC
        """, (mother_id,)).fetchall()

        conn.close()

        return {
            "mother_id": mother_id,
            "status": "ok",
            "vitals": dict(vitals_row) if vitals_row else None,
            "active_flags": [dict(f) for f in flags]
        }

    except Exception as e:
        return {"mother_id": mother_id, "status": "error", "message": str(e)}


def _get_sensor_context_str(mother_id: str) -> str:
    """Format sensor data as a string for injection into agent context."""
    db_path = config.sensor.sqlite_path
    if not os.path.exists(db_path):
        return "No live sensor data available. Raspberry Pi not yet connected."

    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        vitals = conn.execute("""
            SELECT * FROM vitals WHERE mother_id = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (mother_id,)).fetchone()

        flags = conn.execute("""
            SELECT flag_name, severity, reasoning FROM fusion_flags
            WHERE mother_id = ? AND is_active = 1
        """, (mother_id,)).fetchall()

        conn.close()

        if not vitals:
            return "No sensor readings yet for this mother."

        v = dict(vitals)
        lines = [
            f"[LIVE SENSOR DATA]",
            f"Maternal HR: {v.get('maternal_hr', 'N/A')} bpm",
            f"SpO2: {v.get('spo2', 'N/A')}%",
            f"Temperature: {v.get('temperature', 'N/A')}°C",
            f"Fetal HR: {v.get('fetal_hr', 'N/A')} bpm",
            f"Fetal Movement: {v.get('fetal_movement_count_1h', 'N/A')}/hour",
            f"Activity: {v.get('activity_level', 'N/A')}",
        ]

        if flags:
            lines.append("\nACTIVE ALERTS FROM FUSION ENGINE:")
            for f in flags:
                lines.append(f"⚠ {f['flag_name']} [{f['severity']}]: {f['reasoning']}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error reading sensor data: {str(e)}"


if __name__ == "__main__":
    uvicorn.run(app, host=config.api.host, port=config.api.port)