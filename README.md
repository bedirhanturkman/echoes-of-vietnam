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

```text
Frontend React/Vite
  -> archive query form
  -> door transition
  -> /api/pipeline/generate
  -> result visualization and MIDI download

Backend FastAPI
  -> historical archive selection
  -> AI/fallback event analysis
  -> theme similarity mapping
  -> embedding/reduction map
  -> deterministic MIDI generation
  -> /output/*.mid file serving
```

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

## API Endpoint

The frontend uses:

```text
POST /api/pipeline/generate
```

Archive mode fields:

- `use_archive=true`
- `knock=true|false`
- `start_year`
- `end_year`
- `region`
- `threshold`
- `mood`

The response includes events, embedding points, generated melody notes, metadata, all mood
variants, interpretation text, and a downloadable `midiUrl`.

## Screenshots

Add screenshots here before final submission:

- Intro and archive query
- Door transition
- Result map and timeline
- Generated note sequence
- MIDI download panel
