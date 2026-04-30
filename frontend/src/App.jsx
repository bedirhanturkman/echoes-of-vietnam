// src/App.jsx
import { useCallback, useEffect, useRef, useState } from "react";
import IntroSection from "./components/IntroSection";
import UploadSection from "./components/UploadSection";
import DoorTransition from "./components/DoorTransition";
import ProcessingSection from "./components/ProcessingSection";
import ResultSection from "./components/ResultSection";
import AboutSection from "./components/AboutSection";
import { DEFAULT_MOOD } from "./utils/musicGeneration";
import { generateSoundscape } from "./services/api";
import "./App.css";

function App() {
  const [appState, setAppState] = useState("intro"); // intro, upload, processing, result
  const [taskId, setTaskId] = useState(null);
  const [datasetRequest, setDatasetRequest] = useState(null);
  const [generatedMelody, setGeneratedMelody] = useState(null);
  const [pipelineResult, setPipelineResult] = useState(null);
  const [soundscapeVariants, setSoundscapeVariants] = useState({});
  const [backendError, setBackendError] = useState(null);
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
      doorTransition: "door-transition-section",
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

  const handlePipelineStart = useCallback((request) => {
    setDatasetRequest(request);
    setGeneratedMelody(null);
    setPipelineResult(null);
    setSoundscapeVariants({});
    setBackendError(null);
    setPreviewTime(0);
    setIsPreviewing(false);
    setActivePreviewEventId(null);
    hasGeneratedMelodyRef.current = false;
    setTaskId(null);
    setAppState("doorTransition");
  }, []);

  const runBackendGeneration = useCallback(async (request, mood) => {
    setBackendError(null);
    const result = await generateSoundscape(request, mood);
    const variants = result.variants || {};
    const selectedResult = variants[mood] || result;
    setSoundscapeVariants(variants);
    setGeneratedMelody(selectedResult.melody);
    setPipelineResult(selectedResult);
    setAppState("result");
  }, []);

  const handleDoorOpen = useCallback(() => {
    setTaskId(`local-${Date.now()}`);
    setAppState("processing");
    hasGeneratedMelodyRef.current = true;
    runBackendGeneration(datasetRequest, selectedMood).catch((error) => {
      setBackendError(error.message || "Backend generation failed.");
    });
  }, [datasetRequest, runBackendGeneration, selectedMood]);

  const handleMoodChange = useCallback((moodId) => {
    setSelectedMood(moodId);
    setPreviewTime(0);
    setIsPreviewing(false);
    setActivePreviewEventId(null);
    if (appState !== "result") return;

    const selectedResult = soundscapeVariants[moodId];
    if (selectedResult) {
      setGeneratedMelody(selectedResult.melody);
      setPipelineResult(selectedResult);
      return;
    }

    setBackendError("Selected mood variant is not available. Please generate the dataset again.");
  }, [appState, soundscapeVariants]);

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
        appState === "doorTransition" ||
        appState === "processing" ||
        appState === "result") && (
        <UploadSection onPipelineStart={handlePipelineStart} />
      )}

      {appState === "doorTransition" && datasetRequest && (
        <DoorTransition datasetLabel={datasetRequest.label} onKnock={handleDoorOpen} />
      )}

      {appState === "processing" && taskId && (
        <ProcessingSection taskId={taskId} error={backendError} />
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
