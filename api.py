"""FastAPI application. Thin layer over core/ and utils/. Exposes generate, preview, export, reset endpoints."""

import os
import json
import pathlib
from groq import Groq
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv
from core.agent import run_agent_loop, sanitize_prompt
from core.session import session_manager
from utils.preview import render_preview
from utils.export import export_tsx, export_zip

load_dotenv()
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "2"))
TOKENS: dict = json.loads(pathlib.Path("design_system.json").read_text(encoding="utf-8"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI(title="Guided Component Architect")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class GenerateRequest(BaseModel):
    """Request model for component generation endpoint."""
    prompt: str
    session_id: str = "default"


class GenerateResponse(BaseModel):
    """Response model for component generation endpoint."""
    session_id: str
    component_code: str
    status: str
    validation_errors: list[str]
    preview_url: str
    export_tsx_url: str
    export_zip_url: str


@app.get("/")
def health() -> dict:
    """Health check and model info."""
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/generate", response_model=GenerateResponse)
def generate_component(req: GenerateRequest) -> GenerateResponse:
    """Sanitize prompt, run agentic loop, return component and resource URLs."""
    clean_prompt, err = sanitize_prompt(req.prompt)
    if err:
        raise HTTPException(status_code=400, detail=err)
    code, status, errors = run_agent_loop(
        clean_prompt, req.session_id, TOKENS, client, MODEL_NAME, MAX_RETRIES
    )
    return GenerateResponse(
        session_id=req.session_id,
        component_code=code,
        status=status,
        validation_errors=errors,
        preview_url=f"/preview/{req.session_id}",
        export_tsx_url=f"/export/{req.session_id}?format=tsx",
        export_zip_url=f"/export/{req.session_id}?format=zip",
    )


@app.get("/preview/{session_id}", response_class=HTMLResponse)
def preview(session_id: str) -> HTMLResponse:
    """Render Tailwind CDN HTML preview for the session's last component."""
    code = session_manager.get_last_component(session_id)
    if not code:
        return HTMLResponse(
            "<h1 style='color:white;font-family:sans-serif'>No component generated yet for this session.</h1>",
            status_code=404
        )
    return HTMLResponse(render_preview(code, TOKENS))


@app.get("/export/{session_id}")
def export(session_id: str, format: str = "tsx") -> Response:
    """Export session component as .tsx (bytes) or .zip (bytes)."""
    code = session_manager.get_last_component(session_id)
    if not code:
        raise HTTPException(status_code=404, detail="No component found for this session.")
    if format == "zip":
        return Response(
            export_zip(code, TOKENS),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={session_id}.zip"},
        )
    return Response(
        export_tsx(code),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={session_id}.component.tsx"},
    )


@app.get("/reset/{session_id}")
def reset(session_id: str) -> dict:
    """Clear session state for the given session ID."""
    session_manager.reset(session_id)
    return {"status": "session reset", "session_id": session_id}
