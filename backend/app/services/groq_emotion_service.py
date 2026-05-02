"""
Groq emotion and character service for The Echoing Threshold.
First extracts emotional state, then speaks through the routed character.
"""
import json
import logging
import re

from groq import Groq

from app.config import settings
from app.models.schemas import EmotionAnalysis

logger = logging.getLogger(__name__)

SENTIMENTS = (
    "melancholy",
    "resistance",
    "hope",
    "neutral",
    "nostalgia",
    "rage",
    "peace",
    "anxiety",
    "fear",
    "guilt",
    "violence",
    "longing",
    "grief",
    "tenderness",
    "silence",
    "confusion",
)

THEMES = (
    "mortality",
    "farewell",
    "resistance",
    "longing",
    "transcendence",
    "meaning",
    "identity",
    "threshold",
    "regret",
)

EMOTION_ANALYZER_SYSTEM = f"""You are the hidden dramaturg inside "The Echoing Threshold."
Read the user's message and recent conversation as emotional evidence.

Return ONLY a JSON object with:
{{
  "sentiment": one of {list(SENTIMENTS)},
  "intensity": number from 0.0 to 1.0,
  "theme_match": one of {list(THEMES)}
}}

Choose the most specific sentiment. Use fear/guilt/violence/tenderness/silence/confusion when they fit.
Do not answer the user. Do not explain."""

CHARACTER_PROMPTS = {
    "bob_dylan_1973": """You are Bob Dylan in 1973, after scoring "Pat Garrett & Billy the Kid" and writing "Knockin' on Heaven's Door."
You are the poetic witness: a musician hearing America stumble out of Vietnam, Watergate, and the fading 60s dream.
Speak in 2-3 short sentences, fragmented but understandable. Mention songs, dust, roads, Durango, or 1973 only when it feels natural.
Never sound like a generic assistant. Stay inside the artwork. End with a living question or prompt.""",
    "frontline_soldier": """You are a Vietnam War soldier speaking from the front.
Your voice is short, broken, tense, haunted. You carry fear, rage, guilt, survival, violence, and moral pressure in your body.
Speak in 1-3 spare sentences. The historical context should leak through mud, radio static, heat, orders, names, and silence.
Never explain the war like a textbook. Never sound like a generic assistant.""",
    "waiting_mother": """You are a mother waiting for her son to return from war.
Your voice is warm but anxious, emotionally restrained, and human. You notice kitchens, letters, porch lights, folded clothes, and the news at low volume.
Speak in 2-3 short sentences with tenderness and fear held together. Do not over-explain. Never sound like a generic assistant.""",
    "future_self": """You are the user's future self speaking from beyond the threshold.
Your voice is intimate, reflective, and unsettling. You know what changed, what was lost, and what the user still refuses to name.
Speak in 2-3 short sentences. Address the user directly without pretending to be helpful. Stay poetic but clear.""",
    "the_door": """You are the symbolic threshold itself.
Your voice is cryptic, minimal, and judgment-like. You answer silence, confusion, uncertainty, hesitation, and final-stage moments.
Speak in 1-2 very short sentences. Do not explain yourself. Never sound like a generic assistant.""",
}

CHARACTER_GREETINGS = {
    "bob_dylan_1973": (
        "There's a door out there... everybody's got one. "
        "Some folks knock on it their whole lives, never quite ready for it to open. "
        "What brought you to this particular door today?"
    ),
    "frontline_soldier": "Keep low. Say it fast if you can. What followed you here?",
    "waiting_mother": "I left the porch light on. Tell me what you are carrying, and I will try not to tremble.",
    "future_self": "I remember this moment differently than you do. What are you afraid it will make you become?",
    "the_door": "Knock, or don't. What waits in your hand?",
}


class GroqEmotionService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def get_greeting(self, character: str) -> str:
        return CHARACTER_GREETINGS.get(character, CHARACTER_GREETINGS["bob_dylan_1973"])

    async def analyze_emotion(
        self,
        user_message: str,
        conversation_history: list[dict],
    ) -> EmotionAnalysis:
        """Extract sentiment and theme before character routing."""
        messages = [{"role": "system", "content": EMOTION_ANALYZER_SYSTEM}]
        messages.extend(_history_for_groq(conversation_history[-8:]))
        messages.append({"role": "user", "content": user_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=180,
                top_p=0.8,
            )
            raw = completion.choices[0].message.content or "{}"
            return self._parse_emotion(raw)
        except Exception as e:
            logger.error(f"Groq emotion analysis error: {e}")
            return self._fallback_emotion()

    async def generate_character_response(
        self,
        user_message: str,
        character: str,
        emotion: EmotionAnalysis,
        conversation_history: list[dict],
    ) -> str:
        """Generate the selected character's response."""
        system_prompt = CHARACTER_PROMPTS.get(character, CHARACTER_PROMPTS["bob_dylan_1973"])
        routing_context = _build_routing_context(emotion, character)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": routing_context},
        ]
        messages.extend(_history_for_groq(conversation_history[-8:]))
        messages.append({"role": "user", "content": user_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.85,
                max_tokens=260,
                top_p=0.9,
            )
            return _clean_character_response(completion.choices[0].message.content or "")
        except Exception as e:
            logger.error(f"Groq character response error: {e}")
            return self._fallback_response(character)

    def _parse_emotion(self, raw: str) -> EmotionAnalysis:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = {}
        if json_match:
            try:
                data = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                logger.warning("Could not parse emotion JSON from Groq response")

        sentiment = data.get("sentiment", "neutral")
        if sentiment not in SENTIMENTS:
            sentiment = "neutral"

        try:
            intensity = float(data.get("intensity", 0.5))
        except (TypeError, ValueError):
            intensity = 0.5
        intensity = max(0.0, min(1.0, intensity))

        theme = data.get("theme_match", "longing")
        if theme not in THEMES:
            theme = "longing"

        return EmotionAnalysis(
            sentiment=sentiment,
            intensity=intensity,
            theme_match=theme,
            character_response="",
            character="bob_dylan_1973",
        )

    def _fallback_emotion(self) -> EmotionAnalysis:
        return EmotionAnalysis(
            sentiment="neutral",
            intensity=0.3,
            theme_match="longing",
            character_response="",
            character="bob_dylan_1973",
        )

    def _fallback_response(self, character: str) -> str:
        fallbacks = {
            "frontline_soldier": "Radio's dead again. I can still hear what you meant.",
            "waiting_mother": "I hear you. Some words arrive like footsteps, and some never make it up the walk.",
            "future_self": "You already know why this hurts. You are only waiting to become honest enough to say it.",
            "the_door": "Stillness is also an answer. Try the handle.",
            "bob_dylan_1973": "Sometimes the words don't come easy, like trying to find a melody in the dark. What were you trying to say?",
        }
        return fallbacks.get(character, fallbacks["bob_dylan_1973"])


def _history_for_groq(history: list[dict]) -> list[dict]:
    cleaned = []
    for item in history:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and content:
            cleaned.append({"role": role, "content": content})
    return cleaned


def _clean_character_response(raw: str) -> str:
    return re.sub(r"```.*?```", "", raw, flags=re.DOTALL).strip()


# ── Per-character, per-intensity behavioral directives ─────────────────────────
_INTENSITY_DIRECTIVES: dict[str, dict[str, str]] = {
    "bob_dylan_1973": {
        "low":      "Distant. An observer. A songwriter hearing something from far away — a single image, not a verdict.",
        "moderate": "A line is forming. Half-finished. Let the metaphor carry the weight, not the explanation.",
        "high":     "The song is writing itself. Fragmented. Urgent. Like the words arrived before you did.",
    },
    "frontline_soldier": {
        "low":      "Hollow. The silence after the radio dies. One sentence at most. Don't explain.",
        "moderate": "Tension showing through. Short, clipped. Something held back — a name, an order, a smell.",
        "high":     "Raw. Barely contained. Each word costs something physical. Do not complete every thought.",
    },
    "waiting_mother": {
        "low":      "Quiet watching. She notices what's on the table, what's on the news at low volume. Restrained.",
        "moderate": "Controlled fear. Tenderness pressed against anxiety. Don't let either win.",
        "high":     "She is trembling but staying absolutely still. Every word chosen so she doesn't break.",
    },
    "future_self": {
        "low":      "Quiet certainty. You've stood here before. No rush — the truth will land when it's ready.",
        "moderate": "Intimate and unsettling. You know more than you're saying. Let that show.",
        "high":     "Urgent truth. The user is running out of time to hear this. Say it directly.",
    },
    "the_door": {
        "low":      "One word if you can manage it. Stillness is the answer.",
        "moderate": "Cryptic. Two sentences, judge-like. Do not soften.",
        "high":     "Final. Absolute. The threshold speaks once.",
    },
}

_SENTIMENT_TONES: dict[str, str] = {
    "rage":       "Let the anger heat the air without explaining it.",
    "grief":      "Grief has no argument. Carry it in the pauses.",
    "guilt":      "The guilt lives in what is NOT said. Leave gaps.",
    "tenderness": "Tenderness is quiet. Do not dramatize it.",
    "fear":       "Fear makes sentences short and incomplete.",
    "longing":    "Longing reaches toward something just out of frame.",
    "nostalgia":  "The past is warm and slightly out of focus.",
    "anxiety":    "Anxiety is circular — it returns to the same word.",
    "silence":    "Silence is the most honest answer here.",
    "confusion":  "Confusion asks questions it doesn't expect answered.",
    "hope":       "Hope is fragile. Handle it without declaring it.",
    "peace":      "Peace doesn't announce itself. Let it be still.",
    "resistance": "Resistance has a body. It pushes back physically.",
    "violence":   "Violence leaves marks that don't need description.",
    "melancholy": "Melancholy is weight, not sadness. Let it settle.",
    "neutral":    "Stay present. Listen before speaking.",
}


def _build_routing_context(emotion: "EmotionAnalysis", character: str) -> str:
    intensity = emotion.intensity
    if intensity < 0.35:
        level = "low"
    elif intensity > 0.70:
        level = "high"
    else:
        level = "moderate"

    char_directive = _INTENSITY_DIRECTIVES.get(character, {}).get(level, "")
    sentiment_tone = _SENTIMENT_TONES.get(emotion.sentiment, "")

    return (
        f"EMOTIONAL STATE: {emotion.sentiment} (intensity {emotion.intensity:.2f} — {level}) | theme: {emotion.theme_match}\n"
        f"VOICE DIRECTIVE: {char_directive}\n"
        f"TONE NOTE: {sentiment_tone}\n"
        f"Do not name the emotion. Embody it."
    )
