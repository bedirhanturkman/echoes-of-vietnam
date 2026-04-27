"""
Health check endpoint.
"""

from fastapi import APIRouter

from app.config import settings
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if all services are operational."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        services={
            "api": "running",
            "mock_embeddings": "enabled" if settings.USE_MOCK_EMBEDDINGS else "disabled",
            "openai": "configured" if not settings.USE_MOCK_EMBEDDINGS else "not_required",
            "midi_generator": "ready",
        },
    )
