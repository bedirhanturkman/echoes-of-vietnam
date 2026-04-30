import { useEffect, useRef, useState } from "react";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const STEP_INTERVAL_MS = 520;
const LOCAL_STEPS = [
  { name: "archive", description: "Reading historical fragments..." },
  { name: "analysis", description: "Analyzing emotional weight..." },
  { name: "themes", description: "Mapping themes to the threshold..." },
  { name: "harmony", description: "Generating folk-inspired harmony..." },
  { name: "composition", description: "Composing the memory melody..." },
];

export default function ProcessingSection({ taskId, error }) {
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
      setProgressPct(96);
    }, LOCAL_STEPS.length * STEP_INTERVAL_MS));

    return () => {
      timersRef.current.forEach((timer) => window.clearTimeout(timer));
      timersRef.current = [];
    };
  }, [taskId]);

  const displaySteps = steps.length > 0 ? steps : LOCAL_STEPS;

  return (
    <section className="processing-section animate-fade-in" id="processing-section">
      <h2>Opening the Archive...</h2>
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
        {error && (
          <p style={{ color: 'var(--danger)', marginTop: '1rem', fontSize: '0.95rem' }}>
            {error}
          </p>
        )}
      </div>
    </section>
  );
}
