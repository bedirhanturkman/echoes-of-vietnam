"""
Gemini Context Service — The Echoing Threshold
Uses Gemini 1.5 Pro for deep historical context enrichment and music/visual parameter generation.
Takes Groq's emotion analysis and maps it to atmospheric parameters.
"""
import json
import logging
from google import genai
from google.genai import types
from app.config import settings
from app.models.schemas import EmotionAnalysis, MusicParams, VisualParams, HistoricalNote

logger = logging.getLogger(__name__)

# ─── Gemini System Prompt ──────────────────────────────────────────

GEMINI_SYSTEM = """You are an artistic director for "The Echoing Threshold" — a living audio-visual installation about thresholds, farewells, and the liminal spaces between who we were and who we become.

Your role: Given an emotional analysis from a conversation with Bob Dylan (1973), you generate precise atmospheric parameters — music settings and visual environment — that transform the user's emotional state into an immersive experience.

HISTORICAL CONTEXT (1973):
- January: Paris Peace Accords signed. Vietnam War officially ending for the US.
- Bob Dylan scores "Pat Garrett & Billy the Kid" — writes "Knockin' on Heaven's Door"
- Watergate scandal unfolding. Nixon presidency crumbling.
- Counter-culture giving way to disillusionment. The 60s dream fading.
- Vietnam veterans returning to protests, confusion, silence.

MUSICAL DNA (from "Knockin' on Heaven's Door"):
- Core chord progression: G - D - Am / G - D - C
- Tempo range: 58-115 BPM depending on emotional state
- Instruments: acoustic guitar (always base), piano (for grief), harmonika (for hope/resistance)
- Soundscape: radio static (isolation), crowd protest (resistance), silence (transcendence)

VISUAL DNA:
- Color: grey-blue (despair) → warm amber (hope) → stormy dark (resistance) → golden dusk (transcendence)
- Clouds: heavy/dense (grief) → dispersing (hope) → swirling fast (resistance)
- Door: closed (defensive) → ajar (opening) → open (surrender/acceptance)

IMPORTANT: Be dramatic. If a user is sad, make the transition heavy. If they are hopeful, make it bright. Do not stay in the middle.

You MUST respond ONLY with a valid JSON object. No markdown, no explanation. Exactly this structure:
{
  "music_params": {
    "tempo_bpm": <integer 58-115>,
    "key": <string, one of: "Am", "Em", "G", "C", "Dm">,
    "instrument_layer": <string, one of: "piano", "harmonika", "ambient_only">,
    "rhythm_type": <string, one of: "steady", "arpeggio", "syncopated">,
    "chord_progression_type": <string, one of: "melancholy", "hope", "resistance", "neutral", "nostalgia", "rage", "peace", "anxiety">,
    "reverb_intensity": <float 0.0-1.0>,
    "historical_soundscape": <string, one of: "radio_static", "crowd_protest", "silence">,
    "cross_fade_seconds": <float 1.0-3.0>
  },
  "visual_params": {
    "color_palette": <string, one of: "blue_grey", "warm_amber", "stormy_dark", "golden_dusk", "deep_red", "ethereal_white", "sickly_green", "sepia_glow">,
    "cloud_density": <float 0.0-1.0>,
    "door_state": <string, one of: "closed", "ajar", "open">,
    "particle_intensity": <float 0.0-1.0>
  },
  "historical_note": {
    "year": 1973,
    "event": <string, a brief 1973 historical event relevant to the conversation>,
    "connection": <string, how this event connects to what the user expressed>
  }
}
"""

# ─── Static Mapping (Fallback) ────────────────────────────────────

SENTIMENT_FALLBACKS = {
    "melancholy": {
        "music_params": MusicParams(
            tempo_bpm=60, key="Am", instrument_layer="piano", rhythm_type="steady",
            chord_progression_type="melancholy",
            reverb_intensity=0.8, historical_soundscape="radio_static",
            cross_fade_seconds=1.5
        ),
        "visual_params": VisualParams(
            color_palette="blue_grey", cloud_density=0.75,
            door_state="ajar", particle_intensity=0.3
        ),
    },
    "resistance": {
        "music_params": MusicParams(
            tempo_bpm=110, key="Em", instrument_layer="harmonika", rhythm_type="syncopated",
            chord_progression_type="resistance",
            reverb_intensity=0.4, historical_soundscape="crowd_protest",
            cross_fade_seconds=1.0
        ),
        "visual_params": VisualParams(
            color_palette="stormy_dark", cloud_density=0.9,
            door_state="closed", particle_intensity=0.85
        ),
    },
    "hope": {
        "music_params": MusicParams(
            tempo_bpm=85, key="G", instrument_layer="harmonika", rhythm_type="arpeggio",
            chord_progression_type="hope",
            reverb_intensity=0.4, historical_soundscape="silence",
            cross_fade_seconds=2.0
        ),
        "visual_params": VisualParams(
            color_palette="golden_dusk", cloud_density=0.2,
            door_state="open", particle_intensity=0.8
        )
    },
    "nostalgia": {
        "music_params": MusicParams(
            tempo_bpm=70, key="C", instrument_layer="piano", rhythm_type="steady",
            chord_progression_type="nostalgia",
            reverb_intensity=0.7, historical_soundscape="radio_static",
            cross_fade_seconds=2.5
        ),
        "visual_params": VisualParams(
            color_palette="sepia_glow", cloud_density=0.4,
            door_state="ajar", particle_intensity=0.3
        )
    },
    "rage": {
        "music_params": MusicParams(
            tempo_bpm=115, key="Dm", instrument_layer="harmonika", rhythm_type="syncopated",
            chord_progression_type="rage",
            reverb_intensity=0.3, historical_soundscape="crowd_protest",
            cross_fade_seconds=1.0
        ),
        "visual_params": VisualParams(
            color_palette="deep_red", cloud_density=0.9,
            door_state="closed", particle_intensity=1.0
        )
    },
    "peace": {
        "music_params": MusicParams(
            tempo_bpm=55, key="G", instrument_layer="ambient_only", rhythm_type="steady",
            chord_progression_type="peace",
            reverb_intensity=0.9, historical_soundscape="silence",
            cross_fade_seconds=3.0
        ),
        "visual_params": VisualParams(
            color_palette="ethereal_white", cloud_density=0.1,
            door_state="open", particle_intensity=0.1
        )
    },
    "anxiety": {
        "music_params": MusicParams(
            tempo_bpm=95, key="Em", instrument_layer="piano", rhythm_type="syncopated",
            chord_progression_type="anxiety",
            reverb_intensity=0.6, historical_soundscape="radio_static",
            cross_fade_seconds=1.5
        ),
        "visual_params": VisualParams(
            color_palette="sickly_green", cloud_density=0.8,
            door_state="closed", particle_intensity=0.9
        )
    },
    "neutral": {
        "music_params": MusicParams(
            tempo_bpm=72, key="G", instrument_layer="ambient_only",
            reverb_intensity=0.6, historical_soundscape="radio_static",
            cross_fade_seconds=3.0
        ),
        "visual_params": VisualParams(
            color_palette="blue_grey", cloud_density=0.4,
            door_state="ajar", particle_intensity=0.2
        ),
    },
}


class GeminiContextService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.0-flash"

    async def enrich(
        self,
        emotion: EmotionAnalysis,
        user_message: str,
        turn_count: int,
    ) -> tuple[MusicParams, VisualParams, HistoricalNote | None]:
        """
        Take Groq's emotion analysis and generate music + visual params via Gemini.
        Falls back to static mapping if Gemini fails.
        """
        prompt = self._build_prompt(emotion, user_message, turn_count)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=GEMINI_SYSTEM,
                    temperature=0.4,
                    max_output_tokens=512,
                ),
            )
            raw = response.text.strip()
            return self._parse_response(raw, emotion.sentiment)

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback(emotion.sentiment)

    def _build_prompt(self, emotion: EmotionAnalysis, user_message: str, turn: int) -> str:
        return f"""
Conversation turn #{turn}
User said: "{user_message}"
Detected sentiment: {emotion.sentiment} (intensity: {emotion.intensity:.2f})
Theme: {emotion.theme_match}
Character (Bob Dylan 1973) responded: "{emotion.character_response[:200]}..."

Generate the atmospheric parameters for this emotional moment.
The intensity is {emotion.intensity:.2f} — higher intensity means more dramatic visual/audio response.
"""

    def _parse_response(
        self, raw: str, sentiment: str
    ) -> tuple[MusicParams, VisualParams, HistoricalNote | None]:
        """Parse Gemini JSON response into typed models."""
        # Strip possible markdown code fences
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()

        try:
            data = json.loads(clean)
            music = MusicParams(**data["music_params"])
            visual = VisualParams(**data["visual_params"])

            historical_note = None
            if "historical_note" in data and data["historical_note"]:
                historical_note = HistoricalNote(**data["historical_note"])

            return music, visual, historical_note

        except Exception as e:
            logger.warning(f"Could not parse Gemini response: {e}. Using fallback.")
            return self._fallback(sentiment)

    def _fallback(self, sentiment: str) -> tuple[MusicParams, VisualParams, HistoricalNote | None]:
        """Static fallback mapping when Gemini is unavailable."""
        fb = SENTIMENT_FALLBACKS.get(sentiment, SENTIMENT_FALLBACKS["neutral"])
        return fb["music_params"], fb["visual_params"], None

    def get_initial_params(self) -> tuple[MusicParams, VisualParams]:
        """Initial atmospheric params before any conversation."""
        fb = SENTIMENT_FALLBACKS["neutral"]
        return fb["music_params"], fb["visual_params"]
