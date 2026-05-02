# Echoes Through the Door: AI Memory-to-Melody Archive

An interactive digital artwork that turns historical memory into deterministic MIDI composition.
The user does not write events, emotions, or themes. They enter only a date range, a region, or
press **Knock**. The system selects historical fragments from its archive, analyzes emotional and
thematic meaning, maps the results into musical rules, and opens a door-shaped transition into a
generated memory melody.

## Artistic Statement

The project is inspired by the cultural threshold around 1973: the Vietnam War, anti-war
counterculture, farewell, transition, mortality, and legacy. The door metaphor comes from the
idea of a historical threshold: a point where public memory knocks, waits, and becomes sound.

The current conversation mode can use adaptive character routing as part of the artwork:
"The system can let the conversation itself summon the voice." The possible voices are Bob Dylan
in 1973, a frontline soldier, a waiting mother, the user's future self, and the door itself.
Groq first extracts sentiment, intensity, and theme; the router selects the voice; then Gemini
translates the emotional state into music, visuals, and historical context.

The visitor can also choose a voice manually. In Auto mode, Echo chooses from the emotional and
thematic state of the exchange. In manual mode, the selected character answers every message until
the visitor returns control to the threshold. Dialogue follows the chosen voice, music still
responds to emotion and intensity, and the visual atmosphere keeps the selected character's color
world.

Rather than copying Bob Dylan's melodies, the system models broad 1970s folk harmony principles:
simple I-IV-V progressions, acoustic phrasing, descending farewell motifs, and unresolved
transitions.

## User Flow

1. Intro screen
2. Date / region / threshold query screen
3. Door screen with Knock interaction
4. Processing animation
5. Result screen with timeline, embedding map, AI analysis cards, note visualization, silent preview, and MIDI download

The default **Knock** query is:

```text
1968-1975 / Vietnam-USA / farewell
```

## Dataset

The bundled archive lives at:

```text
backend/data/historical_memory_events.json
```

It includes selected events such as:

- 1965 Vietnam War escalation
- 1968 Tet Offensive
- 1969 Woodstock
- 1970 Kent State shootings
- 1973 Paris Peace Accords
- 1973 Pat Garrett & Billy the Kid
- 1975 Fall of Saigon

The dataset stores historical facts and context only. It does not store final user-provided
emotions or themes; those are inferred by the analysis layer.

## AI Techniques

1. **NLP / LLM historical-emotional analysis**
   - `analyzeEventsWithAI()` uses Groq when configured.
   - `fallbackAnalyzeEvents()` keeps the demo working offline with deterministic rules.

2. **Theme similarity / embedding-inspired mapping**
   - Events are scored against farewell, mortality, war, hope, guilt, transition, and legacy.
   - Gemini embeddings are used for semantic map projection when available.
   - A deterministic fallback projection is used when AI services are unavailable.

3. **MIDI / music generation**
   - Each event becomes a motif.
   - Emotion, intensity, historical weight, date, and theme scores influence scale, pitch,
     duration, velocity, chord, bass, harmony, and beat layers.

4. **Visual interpretation**
   - The door transition, embedding map, memory timeline, and generated note sequence show how
     the archive becomes music.

## Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Vite)               │
│                                                         │
│  ConversationPanel ──► useConversation hook             │
│       │                      │                          │
│  AudioEngine (Tone.js)   AtmosphereCanvas               │
│  real-time synthesis     door / color / particles       │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (REST)
          ┌────────────▼────────────────────┐
          │       BACKEND (FastAPI)         │
          │                                 │
          │  POST /conversation/start       │
          │  POST /conversation/message     │
          │                                 │
          │  ┌─────────────────────────┐    │
          │  │    EmotionManager       │    │
          │  │  (session orchestrator) │    │
          │  └────────┬────────────────┘    │
          │           │                     │
          │   ┌───────▼────────┐            │
          │   │ Groq Service   │ ① NLP      │
          │   │ emotion        │ sentiment  │
          │   │ analysis       │ intensity  │
          │   │ (llama-3.3-70b)│ theme      │
          │   └───────┬────────┘            │
          │           │                     │
          │   ┌───────▼────────┐            │
          │   │ Character      │ ② Adaptive │
          │   │ Router         │ scoring:   │
          │   │                │ keyword +  │
          │   │ bob_dylan_1973 │ sentiment  │
          │   │ frontline_     │ + theme +  │
          │   │  soldier       │ intensity  │
          │   │ waiting_mother │ + arc      │
          │   │ future_self    │            │
          │   │ the_door       │            │
          │   └───────┬────────┘            │
          │           │                     │
          │   ┌───────▼────────┐            │
          │   │ Groq Service   │ ③ LLM      │
          │   │ character      │ character  │
          │   │ response gen.  │ voice with │
          │   │ (llama-3.3-70b)│ emotional  │
          │   │                │ directive  │
          │   └───────┬────────┘            │
          │           │                     │
          │   ┌───────▼────────┐            │
          │   │ Gemini Service │ ④ Music /  │
          │   │ atmosphere     │ visual /   │
          │   │ generation     │ historical │
          │   │ (gemini-2.0-   │ parameter  │
          │   │  flash)        │ generation │
          │   └────────────────┘            │
          └─────────────────────────────────┘
```

**AI Pipeline (per message turn):**

| Step | Service | Technique | Output |
|------|---------|-----------|--------|
| ① | Groq `llama-3.3-70b` | NLP sentiment analysis | `sentiment`, `intensity`, `theme_match` |
| ② | Character Router | Rule-based + scoring algorithm | Selected character voice |
| ③ | Groq `llama-3.3-70b` | LLM generation with emotional directive | Character response text |
| ④ | Gemini `gemini-2.0-flash` | Generative parameter synthesis | `MusicParams`, `VisualParams`, `HistoricalNote` |
| ⑤ | Tone.js (frontend) | Real-time generative audio synthesis | Live music responding to emotion |

## Environment

API keys stay only in the backend `.env` file. Do not expose them to the frontend.

Create or update `backend/.env` from `backend/.env.example`:

```text
GEMINI_API_KEY=
GROQ_API_KEY=
USE_MOCK_EMBEDDINGS=True
```

The project still works in fallback mode without live AI APIs.

## How To Run

Backend:

```powershell
cd backend
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## API Endpoints

The current conversation frontend uses:

```text
POST /api/v1/conversation/start
POST /api/v1/conversation/message
GET  /api/v1/conversation/session/{session_id}
GET  /api/v1/health
```

`/conversation/start` opens an adaptive session with Bob Dylan as the first threshold voice.
`/conversation/message` returns the routed character, character response, emotion analysis,
music parameters, visual parameters, historical note, and turn count.

## Screenshots

*(Add before final submission: intro screen, door transition, conversation panel, audio engine active state)*
