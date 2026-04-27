import React, { useEffect, useRef, useState } from "react";
import { CheckCircle2, Circle } from "lucide-react";

const PIPELINE_STEPS = [
  "Reading historical fragments...",
  "Creating semantic embeddings...",
  "Mapping memories into coordinates...",
  "Translating data into notes...",
  "Generating the final soundscape...",
];

const STEP_DURATION_MS = 900;
const FALLBACK_TIMEOUT_MS = 7000;

export default function ProcessingSection({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const hasCompletedRef = useRef(false);
  const timerRefs = useRef([]);

  useEffect(() => {
    hasCompletedRef.current = false;

    const clearTimers = () => {
      timerRefs.current.forEach((timerId) => window.clearTimeout(timerId));
      timerRefs.current = [];
    };

    const finishProcessing = () => {
      if (hasCompletedRef.current) return;

      hasCompletedRef.current = true;
      clearTimers();
      onComplete();
    };

    for (let stepIndex = 1; stepIndex < PIPELINE_STEPS.length; stepIndex += 1) {
      const timerId = window.setTimeout(() => {
        setCurrentStep(stepIndex);
      }, STEP_DURATION_MS * stepIndex);

      timerRefs.current.push(timerId);
    }

    const completionTimerId = window.setTimeout(() => {
      finishProcessing();
    }, STEP_DURATION_MS * PIPELINE_STEPS.length);
    timerRefs.current.push(completionTimerId);

    const fallbackTimerId = window.setTimeout(() => {
      setCurrentStep(PIPELINE_STEPS.length - 1);
      finishProcessing();
    }, FALLBACK_TIMEOUT_MS);
    timerRefs.current.push(fallbackTimerId);

    return () => {
      clearTimers();
    };
  }, [onComplete]);

  return (
    <section
      className="processing-section animate-fade-in"
      id="processing-section"
    >
      <h2>Synthesizing Memories...</h2>
      <div className="progress-container">
        {PIPELINE_STEPS.map((step, index) => {
          let stepClass = "step";
          if (index < currentStep) stepClass += " completed";
          else if (index === currentStep) stepClass += " active";

          return (
            <div key={index} className={stepClass}>
              <div className="step-icon">
                {index < currentStep ? (
                  <CheckCircle2 size={20} />
                ) : (
                  <Circle size={20} />
                )}
              </div>
              <span>{step}</span>
            </div>
          );
        })}

        <div className="progress-bar-bg">
          <div
            className="progress-bar-fill"
            style={{
              width: `${((currentStep + 1) / PIPELINE_STEPS.length) * 100}%`,
            }}
          />
        </div>
      </div>
    </section>
  );
}
