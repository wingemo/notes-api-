import os
import json
import requests
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

# ==========================
# KONFIGURATION
# ==========================

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("MODEL", "mistral")
TIMEOUT = 60

# ==========================
# FASTAPI INIT
# ==========================

app = FastAPI(
    title="Notes AI API",
    version="1.0.0",
    description="REST API som strukturerar anteckningar till JSON"
)

# ==========================
# REQUEST / RESPONSE SCHEMA
# ==========================

class NotesRequest(BaseModel):
    text: str

class NotesResponse(BaseModel):
    title: str
    date: str
    summary: str
    action_items: List[str]

# ==========================
# SYSTEM PROMPT
# ==========================

SYSTEM_PROMPT = """
Du är en professionell assistent.

Uppgift:
1. Rätta stavning och grammatik.
2. Strukturera anteckningarna tydligt.
3. Returnera ENDAST giltig JSON.
4. Ingen förklarande text.
5. Ingen markdown.

JSON schema:
{
  "title": "kort beskrivande titel",
  "date": "YYYY-MM-DD om möjligt annars tom sträng",
  "summary": "kort sammanfattning",
  "action_items": ["lista", "med", "åtgärder"]
}
"""

# ==========================
# AI-FUNKTION
# ==========================

def call_ai(notes: str) -> dict:
    prompt = SYSTEM_PROMPT + "\n\nText:\n" + notes

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()

        raw_output = response.json().get("response", "")
        parsed_json = json.loads(raw_output)

        return parsed_json

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama connection error: {str(e)}"
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON returned from model"
        )

# ==========================
# API ENDPOINTS
# ==========================

@app.get("/")
def health_check():
    return {
        "status": "running",
        "model": MODEL
    }

@app.post("/notes", response_model=NotesResponse)
def process_notes(request: NotesRequest):
    ai_result = call_ai(request.text)

    try:
        validated = NotesResponse(**ai_result)
        return validated

    except ValidationError:
        raise HTTPException(
            status_code=500,
            detail="Model output does not match expected schema"
        )
