"""
Adaptive character routing for The Echoing Threshold.
The conversation summons the voice; the user does not choose it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterProfile:
    id: str
    name: str
    initials: str
    role: str


CHARACTERS = {
    "bob_dylan_1973": CharacterProfile(
        id="bob_dylan_1973",
        name="Bob Dylan",
        initials="BD",
        role="Poetic witness, musician, cultural voice of 1973.",
    ),
    "frontline_soldier": CharacterProfile(
        id="frontline_soldier",
        name="Frontline Soldier",
        initials="FS",
        role="Vietnam War soldier speaking from the front.",
    ),
    "waiting_mother": CharacterProfile(
        id="waiting_mother",
        name="Waiting Mother",
        initials="WM",
        role="A mother waiting for her son to return from war.",
    ),
    "future_self": CharacterProfile(
        id="future_self",
        name="Future Self",
        initials="YF",
        role="The user's future self speaking from beyond the threshold.",
    ),
    "the_door": CharacterProfile(
        id="the_door",
        name="The Door",
        initials="DR",
        role="The symbolic threshold itself.",
    ),
}

MUSIC_TERMS = {
    "bob",
    "dylan",
    "song",
    "songs",
    "music",
    "melody",
    "guitar",
    "harmonica",
    "harmonika",
    "lyric",
    "lyrics",
    "knockin",
    "heaven's door",
    "heavens door",
    "album",
    "singer",
}

SOLDIER_TERMS = {
    "fear",
    "afraid",
    "scared",
    "rage",
    "anger",
    "angry",
    "guilt",
    "guilty",
    "survive",
    "survival",
    "violence",
    "violent",
    "kill",
    "killing",
    "blood",
    "front",
    "soldier",
    "war",
    "gun",
    "moral",
}

MOTHER_TERMS = {
    "hope",
    "longing",
    "grief",
    "grieve",
    "tender",
    "tenderness",
    "care",
    "family",
    "mother",
    "son",
    "home",
    "return",
    "waiting",
    "miss",
    "love",
}

FUTURE_SELF_TERMS = {
    "meaning",
    "mortality",
    "death",
    "identity",
    "regret",
    "threshold",
    "become",
    "future",
    "self",
    "change",
    "transform",
    "transformation",
    "who am i",
    "why",
    "purpose",
}

DOOR_TERMS = {
    "silent",
    "silence",
    "confused",
    "confusion",
    "uncertain",
    "uncertainty",
    "hesitate",
    "hesitation",
    "stuck",
    "lost",
    "nothing",
    "empty",
}

WAITING_MOTHER_SENTIMENTS = {"hope", "longing", "grief", "tenderness", "nostalgia", "melancholy", "peace"}
SOLDIER_SENTIMENTS = {"rage", "anxiety", "fear", "guilt", "violence", "resistance"}
DOOR_SENTIMENTS = {"silence", "neutral", "confusion"}
FUTURE_THEMES = {"mortality", "meaning", "identity", "threshold", "regret", "transcendence"}

# Which character each theme most belongs to, and its score bonus
_THEME_CHARACTER_SCORES: dict[str, tuple[str, int]] = {
    "mortality":     ("frontline_soldier", 6),
    "farewell":      ("waiting_mother",    6),
    "resistance":    ("frontline_soldier", 5),
    "longing":       ("waiting_mother",    6),
    "transcendence": ("the_door",          6),
    "meaning":       ("future_self",       6),
    "identity":      ("future_self",       7),
    "threshold":     ("the_door",          7),
    "regret":        ("future_self",       6),
}

# Bob Dylan gets a cultural co-bonus on certain themes
_DYLAN_THEME_BONUS = {"farewell", "resistance", "transcendence", "longing"}


def select_character(
    sentiment: str,
    intensity: float,
    theme_match: str,
    message: str,
    history: list[dict],
    turn_count: int,
) -> str:
    """Choose the next voice using deterministic, meaningful routing."""
    if turn_count == 0:
        return "bob_dylan_1973"

    text = message.lower()
    recent = _recent_character_ids(history)
    scores: dict[str, float] = {
        "bob_dylan_1973": 0,
        "frontline_soldier": 0,
        "waiting_mother": 0,
        "future_self": 0,
        "the_door": 0,
    }

    # ── Keyword hits ──────────────────────────────────────────────
    if _contains_any(text, MUSIC_TERMS):
        scores["bob_dylan_1973"] += 8
    if _contains_any(text, SOLDIER_TERMS):
        scores["frontline_soldier"] += 6
    if _contains_any(text, MOTHER_TERMS):
        scores["waiting_mother"] += 6
    if _contains_any(text, FUTURE_SELF_TERMS):
        scores["future_self"] += 6
    if _contains_any(text, DOOR_TERMS):
        scores["the_door"] += 6

    # ── Sentiment class ───────────────────────────────────────────
    if sentiment in WAITING_MOTHER_SENTIMENTS:
        scores["waiting_mother"] += 6
    if sentiment in SOLDIER_SENTIMENTS:
        scores["frontline_soldier"] += 6
    if sentiment in DOOR_SENTIMENTS:
        scores["the_door"] += 5

    # ── Theme → character mapping (primary) ──────────────────────
    if theme_match in _THEME_CHARACTER_SCORES:
        char, bonus = _THEME_CHARACTER_SCORES[theme_match]
        scores[char] += bonus
    if theme_match in _DYLAN_THEME_BONUS:
        scores["bob_dylan_1973"] += 3

    # ── Intensity modulation ──────────────────────────────────────
    # High intensity pulls toward raw/visceral voices
    if intensity >= 0.75:
        scores["frontline_soldier"] += 4
        scores["the_door"] -= 2
    elif intensity >= 0.50:
        scores["waiting_mother"] += 2
        scores["bob_dylan_1973"] += 2
    elif intensity < 0.25:
        scores["the_door"] += 5 if turn_count > 2 else 2
        scores["future_self"] += 2

    # ── Conversation arc nudges ───────────────────────────────────
    # Early turns: Dylan holds the floor; later turns open other voices
    if turn_count <= 2:
        scores["bob_dylan_1973"] += 3
    elif turn_count >= 8:
        scores["future_self"] += 2  # Arc bends toward reflection

    # ── Streak prevention (2 consecutive = penalty) ───────────────
    if _same_character_streak(recent, 2):
        scores[recent[-1]] -= 8

    if not any(scores.values()):
        return recent[-1] if recent else "bob_dylan_1973"

    priority = [
        "bob_dylan_1973",
        "frontline_soldier",
        "waiting_mother",
        "future_self",
        "the_door",
    ]
    return max(priority, key=lambda character_id: scores[character_id])


def get_character_name(character_id: str) -> str:
    return CHARACTERS.get(character_id, CHARACTERS["bob_dylan_1973"]).name


def get_character_initials(character_id: str) -> str:
    return CHARACTERS.get(character_id, CHARACTERS["bob_dylan_1973"]).initials


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _recent_character_ids(history: list[dict]) -> list[str]:
    return [
        item.get("character_id")
        for item in history
        if item.get("role") == "assistant" and item.get("character_id")
    ]


def _same_character_streak(recent: list[str], size: int) -> bool:
    return len(recent) >= size and len(set(recent[-size:])) == 1
