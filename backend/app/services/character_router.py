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
    scores = {
        "bob_dylan_1973": 0,
        "frontline_soldier": 0,
        "waiting_mother": 0,
        "future_self": 0,
        "the_door": 0,
    }

    if _contains_any(text, MUSIC_TERMS):
        scores["bob_dylan_1973"] += 7
    if sentiment in WAITING_MOTHER_SENTIMENTS:
        scores["waiting_mother"] += 4
    if sentiment in SOLDIER_SENTIMENTS:
        scores["frontline_soldier"] += 4
    if sentiment in DOOR_SENTIMENTS:
        scores["the_door"] += 3
    if theme_match in FUTURE_THEMES:
        scores["future_self"] += 4

    if _contains_any(text, SOLDIER_TERMS):
        scores["frontline_soldier"] += 4
    if _contains_any(text, MOTHER_TERMS):
        scores["waiting_mother"] += 4
    if _contains_any(text, FUTURE_SELF_TERMS):
        scores["future_self"] += 4
    if _contains_any(text, DOOR_TERMS):
        scores["the_door"] += 4

    if intensity < 0.25 and turn_count > 2:
        scores["the_door"] += 5

    if theme_match in {"farewell", "resistance"}:
        scores["bob_dylan_1973"] += 2
    if theme_match == "longing":
        scores["waiting_mother"] += 2

    if _same_character_streak(recent, 3):
        scores[recent[-1]] -= 5

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
