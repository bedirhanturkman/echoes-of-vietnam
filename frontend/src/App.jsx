// src/App.jsx
import { useCallback, useEffect, useRef, useState } from "react";
import IntroSection from "./components/IntroSection";
import UploadSection from "./components/UploadSection";
import ProcessingSection from "./components/ProcessingSection";
import ResultSection from "./components/ResultSection";
import AboutSection from "./components/AboutSection";
import { DEFAULT_MOOD, generateMelodyFromData, getMusicMetadata } from "./utils/musicGeneration";
import "./App.css";

const CATEGORY_COORDS = {
  conflict: { x: 18, y: 28 },
  peace_talks: { x: 78, y: 78 },
  civilian_impact: { x: 28, y: 36 },
  political_transition: { x: 58, y: 48 },
  uncertainty: { x: 42, y: 55 },
};

const normalizeResultEvents = (events) =>
  events.map((event, index) => {
    const category = String(event.category || "uncertainty");
    const fallback = CATEGORY_COORDS[category] || CATEGORY_COORDS.uncertainty;
    return {
      id: String(event.id || `e${index + 1}`),
      date: String(event.date || ""),
      title: String(event.title || `Historical event ${index + 1}`),
      category,
      sentiment: Number(event.sentiment ?? 0),
      x: Number.isFinite(Number(event.x)) ? Number(event.x) : fallback.x + index * 1.5,
      y: Number.isFinite(Number(event.y)) ? Number(event.y) : fallback.y,
      musicalInterpretation:
        event.musicalInterpretation ||
        "A data-shaped phrase rendered from the generated melody.",
    };
  });

const buildResultFromData = (events, melody, moodId) => {
  return {
    events: normalizeResultEvents(events),
    musicMetadata: getMusicMetadata(melody, moodId),
    interpretationText: `Each historical event contributes to the composition. Semantic/category clusters choose harmonic sections, mood selects scale and tempo, event coordinates influence pitch and velocity, and intensity shapes duration. The final MIDI combines melody, bass, and chord layers.`,
  };
};

function App() {
  const [appState, setAppState] = useState("intro"); // intro, upload, processing, result
  const [taskId, setTaskId] = useState(null);
  const [sourceData, setSourceData] = useState([]);
  const [generatedMelody, setGeneratedMelody] = useState(null);
  const [pipelineResult, setPipelineResult] = useState(null);
  const [selectedMood, setSelectedMood] = useState(DEFAULT_MOOD);
  const [previewTime, setPreviewTime] = useState(0);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [activePreviewEventId, setActivePreviewEventId] = useState(null);
  const hasGeneratedMelodyRef = useRef(false);
  const previewStartRef = useRef(0);
  const previewOffsetRef = useRef(0);
  const previewFrameRef = useRef(null);
  const previewTimeRef = useRef(0);

  useEffect(() => {
    const sectionIdByState = {
      upload: "upload-section",
      processing: "processing-section",
      result: "result-section",
    };

    const sectionId = sectionIdByState[appState];
    if (!sectionId) return undefined;

    const scrollTimeout = window.setTimeout(() => {
      document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth" });
    }, 100);

    return () => {
      window.clearTimeout(scrollTimeout);
    };
  }, [appState]);

  const handleBegin = useCallback(() => {
    setAppState("upload");
  }, []);

  const handlePipelineStart = useCallback((events) => {
    setSourceData(events);
    setGeneratedMelody(null);
    setPipelineResult(null);
    setPreviewTime(0);
    setIsPreviewing(false);
    setActivePreviewEventId(null);
    hasGeneratedMelodyRef.current = false;
    setTaskId(`local-${Date.now()}`);
    setAppState("processing");
  }, []);

  const handleProcessingComplete = useCallback(() => {
    if (hasGeneratedMelodyRef.current) return;
    hasGeneratedMelodyRef.current = true;

    const melody = generateMelodyFromData(sourceData, selectedMood);
    const result = buildResultFromData(sourceData, melody, selectedMood);
    setGeneratedMelody(melody);
    setPipelineResult(result);
    setAppState((currentState) =>
      currentState === "result" ? currentState : "result"
    );
  }, [selectedMood, sourceData]);

  const handleMoodChange = useCallback((moodId) => {
    setSelectedMood(moodId);
    setPreviewTime(0);
    setIsPreviewing(false);
    setActivePreviewEventId(null);
    if (!sourceData.length || appState !== "result") return;

    const melody = generateMelodyFromData(sourceData, moodId);
    setGeneratedMelody(melody);
    setPipelineResult(buildResultFromData(sourceData, melody, moodId));
  }, [appState, sourceData]);

  const totalPreviewDuration = (generatedMelody || []).reduce(
    (latest, note) => Math.max(latest, note.startTime + note.duration),
    0
  );

  useEffect(() => {
    previewTimeRef.current = previewTime;
  }, [previewTime]);

  useEffect(() => {
    if (!isPreviewing || !generatedMelody?.length) return undefined;

    previewStartRef.current = performance.now();
    previewOffsetRef.current = previewTimeRef.current;

    const tick = (now) => {
      const nextTime = previewOffsetRef.current + (now - previewStartRef.current) / 1000;

      if (nextTime >= totalPreviewDuration) {
        setPreviewTime(totalPreviewDuration);
        setIsPreviewing(false);
        setActivePreviewEventId(null);
        return;
      }

      setPreviewTime(nextTime);
      const activeNote = generatedMelody.find(
        (note) =>
          note.eventId &&
          note.startTime <= nextTime &&
          nextTime <= note.startTime + note.duration
      );
      setActivePreviewEventId(activeNote?.eventId || null);
      previewFrameRef.current = requestAnimationFrame(tick);
    };

    previewFrameRef.current = requestAnimationFrame(tick);

    return () => {
      if (previewFrameRef.current) cancelAnimationFrame(previewFrameRef.current);
    };
  }, [generatedMelody, isPreviewing, totalPreviewDuration]);

  const handlePreviewToggle = useCallback(() => {
    if (!generatedMelody?.length) return;

    if (isPreviewing) {
      setIsPreviewing(false);
      return;
    }

    setPreviewTime((currentTime) =>
      currentTime >= totalPreviewDuration ? 0 : currentTime
    );
    setIsPreviewing(true);
  }, [generatedMelody, isPreviewing, totalPreviewDuration]);

  const handlePreviewReset = useCallback(() => {
    setPreviewTime(0);
    setIsPreviewing(false);
    setActivePreviewEventId(null);
  }, []);

  return (
    <div className="app-container">
      <IntroSection onBegin={handleBegin} />

      {(appState === "upload" ||
        appState === "processing" ||
        appState === "result") && (
        <UploadSection onPipelineStart={handlePipelineStart} />
      )}

      {appState === "processing" && taskId && (
        <ProcessingSection taskId={taskId} onComplete={handleProcessingComplete} />
      )}

      {appState === "result" && pipelineResult && (
        <>
          <ResultSection
            result={pipelineResult}
            melody={generatedMelody}
            selectedMood={selectedMood}
            onMoodChange={handleMoodChange}
            previewTime={previewTime}
            isPreviewing={isPreviewing}
            activePreviewEventId={activePreviewEventId}
            onPreviewToggle={handlePreviewToggle}
            onPreviewReset={handlePreviewReset}
          />
          <AboutSection />
        </>
      )}
    </div>
  );
}

export default App;
