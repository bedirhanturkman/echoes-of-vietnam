import { useEffect, useRef, useState } from "react";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const STEP_INTERVAL_MS = 520;
const LOCAL_STEPS = [
  { name: "data_ingestion", description: "Reading historical fragments..." },
  { name: "embedding", description: "Creating semantic embeddings..." },
  { name: "reduction", description: "Mapping memories into coordinates..." },
  { name: "mapping", description: "Translating data into notes..." },
  { name: "generation", description: "Generating the final soundscape..." },
];

export default function ProcessingSection({ taskId, onComplete }) {
  const [steps, setSteps] = useState([]);
  const [progressPct, setProgressPct] = useState(0);
  const hasCompletedRef = useRef(false);
  const timersRef = useRef([]);

  useEffect(() => {
    if (!taskId) return;
    hasCompletedRef.current = false;

    timersRef.current = LOCAL_STEPS.map((_, index) =>
      window.setTimeout(() => {
        setProgressPct(Math.round(((index + 1) / LOCAL_STEPS.length) * 100));
        setSteps(LOCAL_STEPS.map((step, stepIndex) => ({
          ...step,
          status:
            stepIndex < index
              ? "completed"
              : stepIndex === index
                ? "active"
                : "pending",
        })));
      }, index * STEP_INTERVAL_MS)
    );

    timersRef.current.push(window.setTimeout(() => {
      if (hasCompletedRef.current) return;
      hasCompletedRef.current = true;
      setSteps(LOCAL_STEPS.map((step) => ({ ...step, status: "completed" })));
      setProgressPct(100);
      onComplete();
    }, LOCAL_STEPS.length * STEP_INTERVAL_MS));

    return () => {
      timersRef.current.forEach((timer) => window.clearTimeout(timer));
      timersRef.current = [];
    };
  }, [taskId, onComplete]);

  const displaySteps = steps.length > 0 ? steps : LOCAL_STEPS;

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
