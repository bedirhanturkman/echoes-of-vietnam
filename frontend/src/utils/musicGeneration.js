export const MOODS = {
  tired: {
    id: "tired",
    label: "Tired / Accepting",
    tempo: 72,
    scaleName: "A Minor Pentatonic",
    scale: [57, 60, 62, 64, 67],
    progression: ["G", "D", "Am7"],
    motif: [0, 1, -1],
    durationFactor: 1.18,
    velocityBoost: -4,
  },
  dark: {
    id: "dark",
    label: "Dark / Conflict",
    tempo: 96,
    scaleName: "E Minor Pentatonic",
    scale: [52, 55, 57, 59, 62],
    progression: ["Em", "C", "G", "D"],
    motif: [0, -1, 2, -2],
    durationFactor: 0.82,
    velocityBoost: 12,
  },
  hopeful: {
    id: "hopeful",
    label: "Hopeful / Peace",
    tempo: 84,
    scaleName: "G Major Pentatonic",
    scale: [55, 57, 59, 62, 64],
    progression: ["G", "D", "C"],
    motif: [0, 2, 1],
    durationFactor: 0.95,
    velocityBoost: 2,
  },
};

export const DEFAULT_MOOD = "tired";

export const CHORDS = {
  C: [60, 64, 67],
  D: [62, 66, 69],
  Em: [52, 55, 59],
  G: [55, 59, 62],
  Am7: [57, 60, 64, 67],
};

const CATEGORY_SHIFT = {
  conflict: -2,
  civilian_impact: -1,
  uncertainty: 0,
  political_transition: 1,
  peace_talks: 2,
};

const CATEGORY_COLOR = {
  conflict: "#8f3f32",
  peace_talks: "#7c9c72",
  civilian_impact: "#a89c8a",
  political_transition: "#c58b45",
  uncertainty: "#6f8796",
};

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

const hashString = (value) => {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
};

const seededRandom = (seed) => {
  let state = seed >>> 0;
  return () => {
    state += 0x6D2B79F5;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
};

const stableDatasetString = (dataset, moodId) =>
  JSON.stringify({
    moodId,
    events: (Array.isArray(dataset) ? dataset : []).map((event) => ({
      date: event.date ?? "",
      title: event.title ?? "",
      category: event.category ?? "",
      sentiment: event.sentiment ?? "",
      casualties: event.casualties ?? "",
    })),
  });

const secondsPerBeat = (tempo) => 60 / tempo;

const scalePitch = (scale, index, octaveShift = 0) => {
  const octave = Math.floor(index / scale.length);
  const wrapped = ((index % scale.length) + scale.length) % scale.length;
  return clamp(scale[wrapped] + octave * 12 + octaveShift, 36, 96);
};

const note = ({ pitch, startTime, duration, velocity, eventId, category, chord, role }) =>
  Object.freeze({
    id: `${eventId}-${role}-${startTime}-${pitch}`,
    pitch: Math.round(pitch),
    startTime: Number(startTime.toFixed(3)),
    duration: Number(duration.toFixed(3)),
    velocity: Math.round(clamp(velocity, 1, 127)),
    eventId,
    category,
    chord,
    role,
  });

export function getMoodConfig(moodId = DEFAULT_MOOD) {
  return MOODS[moodId] || MOODS[DEFAULT_MOOD];
}

export function getCategoryColor(category) {
  return CATEGORY_COLOR[category] || CATEGORY_COLOR.uncertainty;
}

export function generateMelodyFromData(dataset, moodId = DEFAULT_MOOD) {
  const events = Array.isArray(dataset) ? dataset : [];
  const mood = getMoodConfig(moodId);
  const random = seededRandom(hashString(stableDatasetString(events, mood.id)));
  const beat = secondsPerBeat(mood.tempo);
  const maxCasualties = Math.max(0, ...events.map((event) => Number(event.casualties ?? 0)));
  const notes = [];
  let cursor = 0;

  events.forEach((event, eventIndex) => {
    const eventId = String(event.id || `e${eventIndex + 1}`);
    const category = String(event.category || "uncertainty");
    const sentiment = clamp(Number(event.sentiment ?? 0), -1, 1);
    const casualties = Math.max(0, Number(event.casualties ?? 0));
    const casualtyWeight = maxCasualties > 0 ? casualties / maxCasualties : 0.35;
    const chord = mood.progression[eventIndex % mood.progression.length];
    const chordNotes = CHORDS[chord] || CHORDS.G;
    const motif = mood.motif;
    const baseIndex =
      eventIndex +
      Math.round((sentiment + 1) * 1.5) +
      (CATEGORY_SHIFT[category] ?? 0) +
      Math.floor(random() * 2);
    const phraseBeats = clamp(2.2 + casualtyWeight * 1.2, 2.2, 3.6) * mood.durationFactor;
    const phraseDuration = phraseBeats * beat;
    const velocity = 58 + Math.abs(sentiment) * 18 + casualtyWeight * 22 + mood.velocityBoost;

    notes.push(
      note({
        pitch: chordNotes[0] - 12,
        startTime: cursor,
        duration: phraseDuration,
        velocity: 46 + casualtyWeight * 18 + mood.velocityBoost,
        eventId,
        category,
        chord,
        role: "bass",
      })
    );

    chordNotes.forEach((pitch, chordIndex) => {
      notes.push(
        note({
          pitch,
          startTime: cursor + chordIndex * 0.015,
          duration: phraseDuration * 0.9,
          velocity: 34 + chordIndex * 4,
          eventId,
          category,
          chord,
          role: "chord",
        })
      );
    });

    motif.forEach((offset, motifIndex) => {
      const rhythmJitter = random() > 0.6 ? 0.12 * beat : 0;
      const noteDuration = clamp((0.42 + casualtyWeight * 0.28) * beat, 0.18, 0.72);
      const motifStart = cursor + motifIndex * (0.52 * beat) + rhythmJitter;
      const octaveShift =
        mood.id === "dark" ? -12 : mood.id === "hopeful" && sentiment > -0.3 ? 12 : 0;

      notes.push(
        note({
          pitch: scalePitch(mood.scale, baseIndex + offset + motifIndex, octaveShift),
          startTime: motifStart,
          duration: noteDuration,
          velocity,
          eventId,
          category,
          chord,
          role: "melody",
        })
      );
    });

    cursor += phraseDuration + 0.18;
  });

  return Object.freeze(notes.sort((a, b) => a.startTime - b.startTime || a.pitch - b.pitch));
}

export function getMusicMetadata(melody, moodId = DEFAULT_MOOD) {
  const mood = getMoodConfig(moodId);
  const durationSeconds = (melody || []).reduce(
    (latest, item) => Math.max(latest, item.startTime + item.duration),
    0
  );

  return {
    tempo_bpm: mood.tempo,
    scale_name: mood.scaleName,
    chord_progression: mood.progression.join(" - "),
    mood: mood.label,
    total_notes: melody?.length || 0,
    duration_seconds: Number(durationSeconds.toFixed(1)),
  };
}
