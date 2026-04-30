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


# ---------------------------------------------------------------------------
# General MIDI Instrument Programs — Role-based orchestration palette
# ---------------------------------------------------------------------------

GM_INSTRUMENTS = {
    # Strings layer — sustained harmonic foundation
    "strings_ensemble": 49,     # String Ensemble 1
    "strings_slow":     50,     # String Ensemble 2 (slower attack)
    "cello":            43,     # Cello (solo, dark melody)
    "violin":           41,     # Violin (bright melody)

    # Bass layer — harmonic anchor
    "acoustic_bass":    33,     # Acoustic Bass
    "fingered_bass":    34,     # Electric Bass (finger)

    # Melody / Lead instruments
    "piano":            0,      # Acoustic Grand Piano
    "acoustic_guitar":  25,     # Acoustic Guitar (steel)
    "nylon_guitar":     24,     # Acoustic Guitar (nylon) — Dylan-esque

    # Woodwinds — counter-melody, ornaments
    "flute":            74,     # Flute
    "oboe":             69,     # Oboe (mournful)
    "clarinet":         72,     # Clarinet

    # Brass — accents on high-impact events
    "french_horn":      61,     # French Horn
    "trumpet":          57,     # Trumpet
    "trombone":         58,     # Trombone

    # Arpeggiated / textural
    "harp":             47,     # Orchestral Harp
    "vibraphone":       12,     # Vibraphone
    "celesta":          9,      # Celesta (ethereal)
    "music_box":        11,     # Music Box

    # Pads (for intro/outro atmosphere)
    "pad_warm":         90,     # Pad 3 (polysynth)
    "pad_choir":        92,     # Pad 5 (bowed)
}

# ---------------------------------------------------------------------------
# Category → Lead Melody Instrument
# Each event category produces a different timbre for its melody voice
# ---------------------------------------------------------------------------

CATEGORY_INSTRUMENTS = {
    "conflict":             GM_INSTRUMENTS["cello"],           # 43 — dark, intense
    "peace_talks":          GM_INSTRUMENTS["acoustic_guitar"], # 25 — warm, folk
    "civilian_impact":      GM_INSTRUMENTS["oboe"],            # 69 — mournful, vocal
    "political_transition": GM_INSTRUMENTS["piano"],           # 0  — stately
    "uncertainty":          GM_INSTRUMENTS["vibraphone"],       # 12 — ethereal, ambiguous
}

# ---------------------------------------------------------------------------
# Percussion — General MIDI Drum Map (Channel 10)
# Standard GM drum note numbers
# ---------------------------------------------------------------------------

DRUM_NOTES = {
    "kick":          36,   # Bass Drum 1
    "snare":         38,   # Acoustic Snare
    "side_stick":    37,   # Side Stick (rimshot)
    "closed_hihat":  42,   # Closed Hi-Hat
    "open_hihat":    46,   # Open Hi-Hat
    "ride":          51,   # Ride Cymbal 1
    "crash":         49,   # Crash Cymbal 1
    "floor_tom":     41,   # Low Floor Tom
    "mid_tom":       47,   # Low-Mid Tom
    "tambourine":    54,   # Tambourine
    "shaker":        70,   # Maracas
}

# Rhythm patterns: lists of (drum_note, beat_offset, velocity) per beat
# "low" = gentle pulse, "mid" = moderate groove, "high" = intense
RHYTHM_PATTERNS = {
    "low": [
        # Gentle brush-like pulse — ride + soft kick on downbeat
        (DRUM_NOTES["ride"],     0.0,  45),
        (DRUM_NOTES["ride"],     1.0,  35),
        (DRUM_NOTES["ride"],     2.0,  40),
        (DRUM_NOTES["ride"],     3.0,  35),
        (DRUM_NOTES["kick"],     0.0,  40),
    ],
    "mid": [
        # Moderate groove — kick-snare backbone with hihat
        (DRUM_NOTES["closed_hihat"],  0.0,   50),
        (DRUM_NOTES["closed_hihat"],  0.5,   40),
        (DRUM_NOTES["closed_hihat"],  1.0,   50),
        (DRUM_NOTES["closed_hihat"],  1.5,   40),
        (DRUM_NOTES["closed_hihat"],  2.0,   50),
        (DRUM_NOTES["closed_hihat"],  2.5,   40),
        (DRUM_NOTES["closed_hihat"],  3.0,   50),
        (DRUM_NOTES["closed_hihat"],  3.5,   40),
        (DRUM_NOTES["kick"],          0.0,   70),
        (DRUM_NOTES["kick"],          2.0,   65),
        (DRUM_NOTES["snare"],         1.0,   55),
        (DRUM_NOTES["snare"],         3.0,   55),
    ],
    "high": [
        # Intense — driving kick pattern, open hihat, crash accents
        (DRUM_NOTES["closed_hihat"],  0.0,   70),
        (DRUM_NOTES["closed_hihat"],  0.5,   55),
        (DRUM_NOTES["open_hihat"],    1.0,   65),
        (DRUM_NOTES["closed_hihat"],  1.5,   55),
        (DRUM_NOTES["closed_hihat"],  2.0,   70),
        (DRUM_NOTES["closed_hihat"],  2.5,   55),
        (DRUM_NOTES["open_hihat"],    3.0,   65),
        (DRUM_NOTES["closed_hihat"],  3.5,   55),
        (DRUM_NOTES["kick"],          0.0,   90),
        (DRUM_NOTES["kick"],          1.0,   75),
        (DRUM_NOTES["kick"],          2.0,   90),
        (DRUM_NOTES["kick"],          2.5,   70),
        (DRUM_NOTES["snare"],         1.0,   80),
        (DRUM_NOTES["snare"],         3.0,   80),
        (DRUM_NOTES["crash"],         0.0,   85),
    ],
}

# ---------------------------------------------------------------------------
# Arpeggio patterns — index offsets into chord tones
# Each pattern defines the order of chord-tone indices to cycle through
# ---------------------------------------------------------------------------

ARPEGGIO_PATTERNS = {
    "up":       [0, 1, 2],           # Root → 3rd → 5th
    "down":     [2, 1, 0],           # 5th → 3rd → Root
    "broken":   [0, 2, 1, 0],       # Root → 5th → 3rd → Root
    "rolling":  [0, 1, 2, 1],       # Root → 3rd → 5th → 3rd
    "full":     [0, 1, 2, 1, 0, 2], # Wider arpeggio cycle
}

# ---------------------------------------------------------------------------
# Chord root notes (MIDI) — for bass line generation
# ---------------------------------------------------------------------------

CHORD_ROOTS = {
    "C":   48,   # C3
    "D":   50,   # D3
    "Dm":  50,   # D3
    "E":   52,   # E3
    "Em":  52,   # E3
    "G":   43,   # G2
    "A":   45,   # A2
    "Am":  45,   # A2
    "Am7": 45,   # A2
}


# ---------------------------------------------------------------------------
# Humanization utilities — make MIDI output sound more natural
# ---------------------------------------------------------------------------

import random


def humanize_timing(time: float, amount: float = 0.03) -> float:
    """
    Add subtle random offset to note start time for natural feel.
    Amount is in beats (0.03 ≈ 10ms at 120 BPM).
    """
    offset = random.uniform(-amount, amount)
    return max(0.0, time + offset)


def humanize_velocity(velocity: int, amount: int = 5) -> int:
    """
    Add small random variation to velocity for dynamic realism.
    """
    offset = random.randint(-amount, amount)
    return max(VELOCITY_MIN, min(VELOCITY_MAX, velocity + offset))
