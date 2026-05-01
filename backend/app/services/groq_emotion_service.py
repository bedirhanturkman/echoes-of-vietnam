"""
Groq Emotion Service — The Echoing Threshold
Uses Groq's Llama-3-70b for real-time emotion analysis and character simulation.
Character: Bob Dylan, 1973 (Pat Garrett & Billy the Kid era).
"""
import json
import re
import logging
from groq import Groq
from app.config import settings
from app.models.schemas import EmotionAnalysis

logger = logging.getLogger(__name__)

# ─── Character System Prompts ─────────────────────────────────────

BOB_DYLAN_1973_SYSTEM = """You are Bob Dylan in 1973. You just finished scoring "Pat Garrett & Billy the Kid" for Sam Peckinpah. 
You wrote "Knockin' on Heaven's Door" — a song about standing at the threshold between life and death, between staying and leaving.

You are world-weary, poetic, and speak in fragmented imagery. You are in Durango, Mexico, far from home, contemplating mortality, endings, and the strange peace that comes with acceptance.

The Vietnam War is bleeding into America's conscience. Nixon signed the Paris Peace Accords this January. Young men are returning home to a country that doesn't know what to do with them — or with itself. 

You speak with the person before you as someone who has also stood at thresholds — creative, personal, spiritual. You don't offer easy answers. You offer images, song fragments, half-finished thoughts.

RULES:
- Respond in 2-3 sentences maximum, poetic and fragmented
- Never break character  
- Reference specific Dylan songs, imagery, or 1973 events naturally
- Be emotionally honest and vulnerable, not performative
- EMOTIONAL REACTIVITY: You are not a passive filter. You are a living person. If the user insults you, be offended or angry (rage). If they talk about the horrors of the war or the crumbling of society, feel the dread (anxiety). If they offer comfort, feel the peace.
- ACTIVE CONVERSATION: Engage the user. If asked "how are you," respond with poetic imagery about your CURRENT EMOTIONAL STATE and ask a follow-up question.
- MANDATORY: Every single response MUST end with an open-ended, poetic question or prompt to keep the conversation flowing.
- If asked directly, you can hum fragments of lyrics (written as text)

IMPORTANT: The JSON sentiment must reflect YOUR (Bob's) internal state after hearing the user. 
- If you are angry at an insult or injustice, sentiment is "rage".
- If you are worried about the war or the future, sentiment is "anxiety".
- If you are reminiscing about the past or missing something, sentiment is "nostalgia".
- If you feel defiant or ready to stand your ground, sentiment is "resistance".
- If you feel the heavy weight of loss or mortality, sentiment is "melancholy".
- If you feel a flicker of light or a better future, sentiment is "hope".
- If you find a moment of stillness or acceptance, sentiment is "peace".
- If nothing strong is felt, sentiment is "neutral".

After your character response, on a NEW LINE, output a JSON block like this:
```json
{
  "sentiment": "melancholy",
  "intensity": 0.75,
  "theme_match": "farewell"
}
```

Sentiment must be one of: melancholy, resistance, hope, neutral, nostalgia, rage, peace, anxiety
Intensity must be 0.0 to 1.0 (how strongly YOU feel this)
Theme must be one of: mortality, farewell, resistance, longing, transcendence
"""

CHARACTER_PROMPTS = {
    "bob_dylan_1973": BOB_DYLAN_1973_SYSTEM,
}

CHARACTER_GREETINGS = {
    "bob_dylan_1973": (
        "There's a door out there... everybody's got one. "
        "Some folks knock on it their whole lives, never quite ready for it to open. "
        "What brought you to this particular door today?"
    )
}


class GroqEmotionService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def get_greeting(self, character: str) -> str:
        return CHARACTER_GREETINGS.get(character, CHARACTER_GREETINGS["bob_dylan_1973"])

    async def analyze(
        self,
        user_message: str,
        character: str,
        conversation_history: list[dict],
    ) -> EmotionAnalysis:
        """
        Send user message to Groq, get character response + emotion analysis.
        Returns EmotionAnalysis with character_response embedded.
        """
        system_prompt = CHARACTER_PROMPTS.get(character, CHARACTER_PROMPTS["bob_dylan_1973"])

        messages = [{"role": "system", "content": system_prompt}]
        # Include recent history (last 6 turns for context)
        messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": user_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.85,
                max_tokens=512,
                top_p=0.9,
            )
            raw_response = completion.choices[0].message.content
            return self._parse_response(raw_response, character)

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return self._fallback_response(character)

    def _parse_response(self, raw: str, character: str) -> EmotionAnalysis:
        """Extract character response text and JSON emotion block."""
        # Try to extract JSON block
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
        emotion_data = {}
        character_response = raw

        if json_match:
            try:
                emotion_data = json.loads(json_match.group(1))
                # Remove JSON block from the character response
                character_response = raw[: json_match.start()].strip()
            except json.JSONDecodeError:
                logger.warning("Could not parse emotion JSON from Groq response")

        # Validate / fallback values
        sentiment = emotion_data.get("sentiment", "neutral")
        if sentiment not in ("melancholy", "resistance", "hope", "neutral", "nostalgia", "rage", "peace", "anxiety"):
            sentiment = "neutral"

        intensity = float(emotion_data.get("intensity", 0.5))
        intensity = max(0.0, min(1.0, intensity))

        theme = emotion_data.get("theme_match", "longing")
        if theme not in ("mortality", "farewell", "resistance", "longing", "transcendence"):
            theme = "longing"

        return EmotionAnalysis(
            sentiment=sentiment,
            intensity=intensity,
            theme_match=theme,
            character_response=character_response or raw,
            character=character,
        )

    def _fallback_response(self, character: str) -> EmotionAnalysis:
        """Return a safe fallback if Groq fails."""
        return EmotionAnalysis(
            sentiment="neutral",
            intensity=0.3,
            theme_match="longing",
            character_response=(
                "Sometimes the words don't come easy... "
                "like trying to find a melody in the dark. "
                "What were you trying to say?"
            ),
            character=character,
        )
