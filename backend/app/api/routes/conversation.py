"""
Conversation API Routes — The Echoing Threshold
Exposes the Groq+Gemini pipeline via REST endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    StartSessionRequest,
    StartSessionResponse,
    MessageRequest,
    ThresholdResponse,
)
from app.services.emotion_manager import EmotionManager

router = APIRouter()

# ─── Dependency: Shared EmotionManager instance ───────────────────
_manager: EmotionManager | None = None


def get_manager() -> EmotionManager:
    global _manager
    if _manager is None:
        _manager = EmotionManager()
    return _manager


# ─── Endpoints ────────────────────────────────────────────────────

@router.post("/start", response_model=StartSessionResponse, summary="Start a new conversation session")
async def start_session(
    request: StartSessionRequest,
    manager: EmotionManager = Depends(get_manager),
) -> StartSessionResponse:
    """
    Initializes a new conversation session with the chosen character.
    Returns session_id, character greeting, and initial visual/music params.
    """
    session_id = manager.create_session(request.character)
    return manager.get_start_response(session_id, request.character)


@router.post("/message", response_model=ThresholdResponse, summary="Send a message and get atmospheric response")
async def send_message(
    request: MessageRequest,
    manager: EmotionManager = Depends(get_manager),
) -> ThresholdResponse:
    """
    Processes user message through Groq (emotion+character) → Gemini (atmosphere).
    Returns full ThresholdResponse with character reply + music/visual params.
    """
    try:
        return await manager.process_message(
            session_id=request.session_id,
            user_message=request.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/session/{session_id}", summary="Get session info")
async def get_session(
    session_id: str,
    manager: EmotionManager = Depends(get_manager),
):
    """Returns session metadata and turn count."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "character": session["character"],
        "turn_count": session["turn_count"],
        "created_at": session["created_at"],
        "last_emotion": session["last_emotion"],
    }
