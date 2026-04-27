// C:/Users/bdrhn/OneDrive/Masaüstü/UI/echoes-of-vietnam/src/App.jsx
import React, { useCallback, useEffect, useState } from "react";
import IntroSection from "./components/IntroSection";
import UploadSection from "./components/UploadSection";
import ProcessingSection from "./components/ProcessingSection";
import ResultSection from "./components/ResultSection";
import AboutSection from "./components/AboutSection";
import "./App.css";

function App() {
  const [appState, setAppState] = useState("intro"); // intro, upload, processing, result

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

  const handleSampleSelect = useCallback(() => {
    setAppState("processing");
  }, []);

  const handleProcessingComplete = useCallback(() => {
    setAppState((currentState) =>
      currentState === "result" ? currentState : "result"
    );
  }, []);

  return (
    <div className="app-container">
      <IntroSection onBegin={handleBegin} />

      {(appState === "upload" ||
        appState === "processing" ||
        appState === "result") && (
        <UploadSection onSampleSelect={handleSampleSelect} />
      )}

      {appState === "processing" && (
        <ProcessingSection onComplete={handleProcessingComplete} />
      )}

      {appState === "result" && (
        <>
          <ResultSection />
          <AboutSection />
        </>
      )}
    </div>
  );
}

export default App;
