const API_BASE = "/api/pipeline";

const MOOD_TO_BACKEND = {
  tired: "tired_accepting",
  dark: "dark_conflict",
  hopeful: "hopeful_peace",
};

const normalizeVariant = (data) => ({
  events: data.events || [],
  embeddingPoints: data.embeddingPoints || [],
  melody: data.melody || [],
  musicMetadata: {
    tempo_bpm: data.metadata?.tempo || 0,
    scale_name: data.metadata?.scale || "Unknown",
    chord_progression: data.metadata?.progression || "Unknown",
    mood: data.metadata?.mood || "Unknown",
    total_notes: data.metadata?.noteCount || 0,
    duration_seconds: data.metadata?.duration || 0,
    ai: data.metadata?.ai || {},
    archiveQuery: data.metadata?.archiveQuery || {},
    folkInspiration: data.metadata?.folkInspiration || "",
  },
  midiUrl: data.midiUrl,
  interpretationText:
    data.interpretationText ||
    "Each historical event contributes to the composition. The backend maps data into melody, bass, and chord layers, then writes the final MIDI file for download.",
});

const normalizeResponse = (data) => {
  const variants = Object.fromEntries(
    Object.entries(data.variants || {}).map(([mood, variant]) => [
      mood,
      normalizeVariant(variant),
    ])
  );

  return {
    ...normalizeVariant(data),
    selectedMood: data.selectedMood,
    variants,
  };
};

export async function generateSoundscape(datasetRequest, mood) {
  const formData = new FormData();
  formData.append("mood", MOOD_TO_BACKEND[mood] || MOOD_TO_BACKEND.tired);

  if (datasetRequest?.type === "sample") {
    formData.append("use_sample", "true");
  } else if (datasetRequest?.type === "archive") {
    formData.append("use_archive", "true");
    formData.append("knock", datasetRequest.knock ? "true" : "false");
    formData.append("start_year", String(datasetRequest.startYear || 1968));
    formData.append("end_year", String(datasetRequest.endYear || 1975));
    formData.append("region", datasetRequest.region || "Vietnam USA");
    formData.append("threshold", datasetRequest.threshold || "farewell");
  } else if (datasetRequest?.file) {
    formData.append("file", datasetRequest.file);
    formData.append("use_sample", "false");
  } else {
    throw new Error("No dataset selected.");
  }

  let response;
  try {
    response = await fetch(`${API_BASE}/generate`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error("Backend is not available. Please start the backend server.");
  }

  if (!response.ok) {
    let message = "Backend generation failed.";
    try {
      const errorData = await response.json();
      message = errorData.detail || message;
    } catch {
      // Keep default message when backend returns non-JSON.
    }
    throw new Error(message);
  }

  return normalizeResponse(await response.json());
}
