import { useEffect, useRef, useState } from 'react';

export default function DoorTransition({ datasetLabel, onKnock }) {
  const [isOpening, setIsOpening] = useState(false);
  const timeoutRef = useRef(null);

  useEffect(() => () => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
  }, []);

  const handleKnock = () => {
    if (isOpening) return;

    setIsOpening(true);
    timeoutRef.current = window.setTimeout(() => {
      onKnock();
    }, 1450);
  };

  return (
    <section className="door-transition-section animate-fade-in" id="door-transition-section">
      <div className={`upload-card door-card ${isOpening ? 'opening' : ''}`}>
        <h2>The Threshold</h2>
        <p className="door-poem">The data has reached the threshold.</p>
        <p className="door-poem muted">Knock to transform memory into sound.</p>

        <div className="door-scene" aria-hidden="true">
          <div className="door-light" />
          <div className="door-frame">
            <div className="door-panel">
              <span className="door-knob" />
              <span className="door-grain one" />
              <span className="door-grain two" />
            </div>
          </div>
        </div>

        <div className="door-status">
          <span>{isOpening ? "The threshold opens." : "The door waits."}</span>
          <span>{datasetLabel || "Dataset ready"}</span>
        </div>

        <button className="primary-btn door-btn" onClick={handleKnock} disabled={isOpening}>
          {isOpening ? "Opening..." : "Knock"}
        </button>
      </div>
    </section>
  );
}
