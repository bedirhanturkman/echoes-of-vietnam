"""
Emotion Manager for The Echoing Threshold.
Routes each turn through emotion analysis, adaptive character selection, and atmosphere generation.
"""
import logging
import uuid
from datetime import datetime

from app.models.schemas import EmotionAnalysis, StartSessionResponse, ThresholdResponse
from app.services.character_router import CHARACTERS, get_character_name, select_character
from app.services.gemini_context_service import GeminiContextService
from app.services.groq_emotion_service import GroqEmotionService

logger = logging.getLogger(__name__)

_sessions: dict[str, dict] = {}

CHARACTER_PALETTES = {
    "bob_dylan_1973": "sepia_glow",
    "frontline_soldier": "deep_red",
    "waiting_mother": "warm_amber",
    "future_self": "cold_violet",
    "the_door": "threshold_gold",
}


class EmotionManager:
    """
    Orchestrates the adaptive Groq -> router -> Groq -> Gemini pipeline.
    Single instance via FastAPI dependency injection.
    """

    def __init__(self):
        self.groq = GroqEmotionService()
        self.gemini = GeminiContextService()

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            "current_character": "bob_dylan_1973",
            "character_history": ["bob_dylan_1973"],
            "routing_mode": "auto",
            "selected_character": None,
            "history": [],
            "turn_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "last_emotion": None,
        }
        logger.info(f"Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> dict | None:
        return _sessions.get(session_id)

    def get_start_response(self, session_id: str) -> StartSessionResponse:
        character = "bob_dylan_1973"
        greeting = self.groq.get_greeting(character)
        music, visual = self.gemini.get_initial_params()
        visual.color_palette = CHARACTER_PALETTES[character]
        return StartSessionResponse(
            session_id=session_id,
            character_id=character,
            character_name=get_character_name(character),
            greeting=greeting,
            initial_visual=visual,
            initial_music=music,
        )

    async def process_message(
        self,
        session_id: str,
        user_message: str,
        selected_character: str | None = None,
    ) -> ThresholdResponse:
        """
        Full pipeline for one conversation turn:
        1. Groq extracts emotion and theme.
        2. Router selects the character summoned by the conversation.
        3. Groq generates that character's response.
        4. Gemini generates music and visual parameters.
        """
        session = _sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        history = session["history"]
        previous_turn_count = session["turn_count"]
        turn = previous_turn_count + 1

        emotion: EmotionAnalysis = await self.groq.analyze_emotion(
            user_message=user_message,
            conversation_history=history,
        )

        manual_character = _normalize_selected_character(selected_character)
        if manual_character:
            character = manual_character
            routing_mode = "manual"
        else:
            character = select_character(
                sentiment=emotion.sentiment,
                intensity=emotion.intensity,
                theme_match=emotion.theme_match,
                message=user_message,
                history=history,
                turn_count=previous_turn_count,
            )
            routing_mode = "auto"

        character_response = await self.groq.generate_character_response(
            user_message=user_message,
            character=character,
            emotion=emotion,
            conversation_history=history,
        )
        emotion.character = character
        emotion.character_response = character_response

        music_params, visual_params, historical_note = await self.gemini.enrich(
            emotion=emotion,
            user_message=user_message,
            turn_count=turn,
        )
        visual_params.color_palette = CHARACTER_PALETTES.get(character, visual_params.color_palette)

        history.append({"role": "user", "content": user_message})
        history.append(
            {
                "role": "assistant",
                "content": character_response,
                "character_id": character,
                "character_name": get_character_name(character),
            }
        )
        session["turn_count"] = turn
        session["last_emotion"] = emotion.sentiment
        session["current_character"] = character
        session["routing_mode"] = routing_mode
        session["selected_character"] = manual_character
        session["character_history"].append(character)

        if len(history) > 20:
            session["history"] = history[-20:]
        if len(session["character_history"]) > 20:
            session["character_history"] = session["character_history"][-20:]

        return ThresholdResponse(
            session_id=session_id,
            character_id=character,
            character_name=get_character_name(character),
            character_response=character_response,
            emotion=emotion,
            music_params=music_params,
            visual_params=visual_params,
            historical_note=historical_note,
            turn_count=turn,
        )


def _normalize_selected_character(selected_character: str | None) -> str | None:
    if not selected_character:
        return None

    value = selected_character.strip()
    if value == "auto":
        return None
    if value in CHARACTERS:
        return value
    return None
