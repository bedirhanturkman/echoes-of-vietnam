import React, { useEffect, useRef, useState } from "react";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const API_BASE = "/api/v1/pipeline";
const POLL_INTERVAL_MS = 800;

export default function ProcessingSection({ taskId, onComplete }) {
  const [steps, setSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [progressPct, setProgressPct] = useState(0);
  const hasCompletedRef = useRef(false);
  const pollRef = useRef(null);

  useEffect(() => {
    if (!taskId) return;
    hasCompletedRef.current = false;

    const pollStatus = async () => {
      try {
        const statusRes = await fetch(`${API_BASE}/status/${taskId}`);
        if (!statusRes.ok) return;

        const statusData = await statusRes.json();
        setSteps(statusData.steps || []);
        setCurrentStep(statusData.current_step);
        setProgressPct(statusData.progress_pct);

        if (statusData.status === "completed" && !hasCompletedRef.current) {
          hasCompletedRef.current = true;
          clearInterval(pollRef.current);

          // Fetch full result
          const resultRes = await fetch(`${API_BASE}/result/${taskId}`);
          if (resultRes.ok) {
            const resultData = await resultRes.json();
            onComplete(resultData);
          }
        }

        if (statusData.status === "failed") {
          hasCompletedRef.current = true;
          clearInterval(pollRef.current);
          console.error("Pipeline failed:", statusData.error);
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    };

    // Initial poll
    pollStatus();

    // Start polling interval
    pollRef.current = setInterval(pollStatus, POLL_INTERVAL_MS);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [taskId, onComplete]);

  // Fallback step labels if API hasn't responded yet
  const displaySteps =
    steps.length > 0
      ? steps
      : [
          { name: "data_ingestion", description: "Reading historical fragments...", status: "pending" },
          { name: "embedding", description: "Creating semantic embeddings...", status: "pending" },
          { name: "reduction", description: "Mapping memories into coordinates...", status: "pending" },
          { name: "mapping", description: "Translating data into notes...", status: "pending" },
          { name: "generation", description: "Generating the final soundscape...", status: "pending" },
        ];

  return (
    <section className="processing-section animate-fade-in" id="processing-section">
      <h2>Synthesizing Memories...</h2>
      <div className="progress-container">
        {displaySteps.map((step, index) => {
          let stepClass = "step";
          if (step.status === "completed") stepClass += " completed";
          else if (step.status === "active") stepClass += " active";

          return (
            <div key={index} className={stepClass}>
              <div className="step-icon">
                {step.status === "completed" ? (
                  <CheckCircle2 size={20} />
                ) : step.status === "active" ? (
                  <Loader2 size={20} className="spin-icon" />
                ) : (
                  <Circle size={20} />
                )}
              </div>
              <span>{step.description}</span>
            </div>
          );
        })}

        <div className="progress-bar-bg">
          <div
            className="progress-bar-fill"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>
    </section>
  );
}
