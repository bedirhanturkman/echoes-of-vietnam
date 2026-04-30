"""
FastAPI application entry point — The Echoing Threshold
An immersive audio-visual installation driven by Groq + Gemini AI.
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import conversation, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure output directory exists."""
    output_path = Path(settings.OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    print("=" * 50)
    print("  THE ECHOING THRESHOLD  v2.0")
    print("=" * 50)
    print(f"  Groq API  : {'OK - Configured' if settings.GROQ_API_KEY else 'MISSING'}")
    print(f"  Gemini API: {'OK - Configured' if settings.GEMINI_API_KEY else 'MISSING'}")
    print(f"  Character : {settings.DEFAULT_CHARACTER}")
    print("=" * 50)
    yield


app = FastAPI(
    title="The Echoing Threshold",
    description=(
        "A living audio-visual installation — the user's emotional state "
        "reshapes the atmosphere in real time via Groq + Gemini AI."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (output dir) ─────────────────────────────────────
output_path = Path(settings.OUTPUT_DIR)
output_path.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=str(output_path)), name="output")

# ── Routes ────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(conversation.router, prefix="/api/v1/conversation", tags=["Conversation"])


@app.get("/", include_in_schema=False)
async def root():
    return {
        "project": "The Echoing Threshold",
        "description": "A living AI-powered audio-visual installation",
        "docs": "/docs",
        "version": "2.0.0",
        "models": {
            "emotion_analysis": "Groq / llama-3-70b-8192",
            "context_enrichment": "Gemini 1.5 Pro",
        },
    }
