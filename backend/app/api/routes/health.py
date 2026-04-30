"""
Health check endpoint — The Echoing Threshold
"""
from fastapi import APIRouter
from app.config import settings
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if all AI services are configured and operational."""
    return HealthResponse(
        status="ok",
        groq_configured=bool(settings.GROQ_API_KEY),
        gemini_configured=bool(settings.GEMINI_API_KEY),
        version="2.0.0",
    )
