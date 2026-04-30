"""
Emotion Manager — The Echoing Threshold
Main orchestrator: routes user messages through Groq → Gemini pipeline.
Maintains session state and conversation history.
"""
import uuid
import logging
from datetime import datetime
from app.services.groq_emotion_service import GroqEmotionService
from app.services.gemini_context_service import GeminiContextService
from app.models.schemas import (
    ThresholdResponse,
    StartSessionResponse,
    EmotionAnalysis,
)

logger = logging.getLogger(__name__)

# ─── In-memory session store ──────────────────────────────────────
# In production this would be Redis; for this installation, memory is fine.
_sessions: dict[str, dict] = {}


class EmotionManager:
    """
    Orchestrates the Groq → Gemini pipeline.
    Single instance (singleton pattern via FastAPI dependency injection).
    """

    def __init__(self):
        self.groq = GroqEmotionService()
        self.gemini = GeminiContextService()

    # ── Session Management ─────────────────────────────────────────

    def create_session(self, character: str) -> str:
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            "character": character,
            "history": [],          # list of {role, content} for Groq context
            "turn_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "last_emotion": None,
        }
        logger.info(f"Session created: {session_id} | character: {character}")
        return session_id

    def get_session(self, session_id: str) -> dict | None:
        return _sessions.get(session_id)

    def get_start_response(self, session_id: str, character: str) -> StartSessionResponse:
        greeting = self.groq.get_greeting(character)
        music, visual = self.gemini.get_initial_params()
        return StartSessionResponse(
            session_id=session_id,
            character=character,
            greeting=greeting,
            initial_visual=visual,
            initial_music=music,
        )

    # ── Main Pipeline ──────────────────────────────────────────────

    async def process_message(
        self, session_id: str, user_message: str
    ) -> ThresholdResponse:
        """
        Full pipeline for one conversation turn:
        1. Groq: emotion analysis + character response
        2. Gemini: music + visual parameters
        3. Return unified ThresholdResponse
        """
        session = _sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        character = session["character"]
        history = session["history"]
        turn = session["turn_count"] + 1

        # ── Step 1: Groq Analysis ──────────────────────────────────
        emotion: EmotionAnalysis = await self.groq.analyze(
            user_message=user_message,
            character=character,
            conversation_history=history,
        )

        # ── Step 2: Gemini Enrichment ──────────────────────────────
        music_params, visual_params, historical_note = await self.gemini.enrich(
            emotion=emotion,
            user_message=user_message,
            turn_count=turn,
        )

        # ── Step 3: Update Session ─────────────────────────────────
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": emotion.character_response})
        session["turn_count"] = turn
        session["last_emotion"] = emotion.sentiment

        # Keep history manageable (last 20 messages)
        if len(history) > 20:
            session["history"] = history[-20:]

        return ThresholdResponse(
            session_id=session_id,
            emotion=emotion,
            music_params=music_params,
            visual_params=visual_params,
            historical_note=historical_note,
            turn_count=turn,
        )
