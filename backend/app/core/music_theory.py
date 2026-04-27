"""
Music theory constants and utilities.
Contains Bob Dylan chord progressions, pentatonic scales,
and mapping rules for data-to-music conversion.
"""

# ---------------------------------------------------------------------------
# Bob Dylan Chord Progressions
# Each progression is a list of chord names used in different musical contexts
# ---------------------------------------------------------------------------

DYLAN_PROGRESSIONS = {
    "knockin_verse": {
        "name": "Knockin' on Heaven's Door — Verse",
        "chords": ["G", "D", "Am7"],
        "mood": "melancholic / reflective",
        "sentiment_range": (-1.0, -0.3),  # Assigned to negative sentiment clusters
    },
    "knockin_chorus": {
        "name": "Knockin' on Heaven's Door — Chorus",
        "chords": ["G", "D", "C"],
        "mood": "hopeful / bittersweet",
        "sentiment_range": (-0.3, 0.3),  # Assigned to neutral sentiment clusters
    },
    "blowin_wind": {
        "name": "Blowin' in the Wind",
        "chords": ["G", "C", "G", "D"],
        "mood": "questioning / open",
        "sentiment_range": (0.3, 1.0),  # Assigned to positive sentiment clusters
    },
}

# ---------------------------------------------------------------------------
# Pentatonic Scales — MIDI note numbers
# ---------------------------------------------------------------------------

PENTATONIC_SCALES = {
    "C_major_pentatonic": {
        "name": "C Major Pentatonic",
        "notes": [60, 62, 64, 67, 69],    # C4, D4, E4, G4, A4
        "note_names": ["C", "D", "E", "G", "A"],
        "tonality": "major",
    },
    "A_minor_pentatonic": {
        "name": "A Minor Pentatonic",
        "notes": [57, 60, 62, 64, 67],     # A3, C4, D4, E4, G4
        "note_names": ["A", "C", "D", "E", "G"],
        "tonality": "minor",
    },
    "D_minor_pentatonic": {
        "name": "D Minor Pentatonic",
        "notes": [62, 65, 67, 69, 72],     # D4, F4, G4, A4, C5
        "note_names": ["D", "F", "G", "A", "C"],
        "tonality": "minor",
    },
    "G_major_pentatonic": {
        "name": "G Major Pentatonic",
        "notes": [55, 57, 59, 62, 64],     # G3, A3, B3, D4, E4
        "note_names": ["G", "A", "B", "D", "E"],
        "tonality": "major",
    },
}

# ---------------------------------------------------------------------------
# Chord-to-MIDI mappings (root + intervals)
# ---------------------------------------------------------------------------

CHORD_MIDI = {
    "C":   [60, 64, 67],        # C  E  G
    "D":   [62, 66, 69],        # D  F# A
    "Dm":  [62, 65, 69],        # D  F  A
    "E":   [64, 68, 71],        # E  G# B
    "Em":  [64, 67, 71],        # E  G  B
    "G":   [55, 59, 62],        # G  B  D
    "A":   [57, 61, 64],        # A  C# E
    "Am":  [57, 60, 64],        # A  C  E
    "Am7": [57, 60, 64, 67],    # A  C  E  G
}

# ---------------------------------------------------------------------------
# Velocity and duration boundaries
# ---------------------------------------------------------------------------

VELOCITY_MIN = 40
VELOCITY_MAX = 120

DURATION_MIN = 0.25   # sixteenth note (in beats)
DURATION_MAX = 4.0    # whole note (in beats)

TEMPO_MIN = 50
TEMPO_MAX = 140

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def select_scale_by_sentiment(avg_sentiment: float) -> dict:
    """
    Choose a pentatonic scale based on overall sentiment.
    Negative sentiment → minor scale, positive → major scale.
    """
    if avg_sentiment < -0.2:
        return PENTATONIC_SCALES["A_minor_pentatonic"]
    elif avg_sentiment < 0.2:
        return PENTATONIC_SCALES["D_minor_pentatonic"]
    else:
        return PENTATONIC_SCALES["C_major_pentatonic"]


def select_progression_by_sentiment(sentiment: float) -> dict:
    """
    Choose a Dylan chord progression based on cluster sentiment.
    """
    for key, prog in DYLAN_PROGRESSIONS.items():
        low, high = prog["sentiment_range"]
        if low <= sentiment <= high:
            return prog
    # Default fallback
    return DYLAN_PROGRESSIONS["knockin_chorus"]


def midi_note_to_name(midi_note: int) -> str:
    """Convert MIDI note number to human-readable name."""
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = (midi_note // 12) - 1
    name = note_names[midi_note % 12]
    return f"{name}{octave}"
