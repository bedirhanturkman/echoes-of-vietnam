"""
FastAPI application entry point.
Sets up CORS, static file serving, and route registration.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import pipeline, visualization, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create output directory on startup."""
    output_path = Path(settings.OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Output directory ready: {output_path.resolve()}")
    print(f"[MUSIC] Mock embeddings: {'ON' if settings.USE_MOCK_EMBEDDINGS else 'OFF'}")
    yield


app = FastAPI(
    title="Echoes of the Vietnam Frontier",
    description="Data sonification API — transforms historical war records into music",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files (serve generated MIDI/WAV) ---
output_path = Path(settings.OUTPUT_DIR)
output_path.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=str(output_path)), name="output")

# --- Register routers ---
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["Pipeline"])
app.include_router(visualization.router, prefix="/api/v1/viz", tags=["Visualization"])


@app.get("/", include_in_schema=False)
async def root():
    return {
        "project": "Echoes of the Vietnam Frontier",
        "description": "Data sonification API",
        "docs": "/docs",
    }
