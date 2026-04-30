/**
 * ThresholdDoor — The Echoing Threshold
 * The central animated SVG door. State: closed | ajar | open.
 * Clicking it in intro phase triggers session start.
 */
import { useEffect, useRef, useState } from 'react';

const DOOR_ANGLES = {
  closed: 0,
  ajar: -35,
  open: -85,
};

const HALO_COLORS = {
  blue_grey: '#4a7fa5',
  warm_amber: '#e8854a',
  stormy_dark: '#2a3a5c',
  golden_dusk: '#d4a044',
};

export default function ThresholdDoor({
  doorState = 'closed',
  colorPalette = 'blue_grey',
  intensity = 0.5,
  isIntro = false,
  onKnock = null,
  isLoading = false,
}) {
  const [currentAngle, setCurrentAngle] = useState(DOOR_ANGLES[doorState]);
  const [isKnocking, setIsKnocking] = useState(false);
  const [haloOpacity, setHaloOpacity] = useState(0.3);
  const animRef = useRef(null);

  // Smoothly animate door angle
  useEffect(() => {
    const target = DOOR_ANGLES[doorState] ?? 0;
    let current = currentAngle;
    cancelAnimationFrame(animRef.current);

    const animate = () => {
      const diff = target - current;
      if (Math.abs(diff) < 0.3) {
        setCurrentAngle(target);
        return;
      }
      current += diff * 0.06;
      setCurrentAngle(current);
      animRef.current = requestAnimationFrame(animate);
    };
    animRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animRef.current);
  }, [doorState]);

  // Halo breathes with intensity
  useEffect(() => {
    setHaloOpacity(0.2 + intensity * 0.6);
  }, [intensity]);

  const handleClick = () => {
    if (!isIntro || isLoading || !onKnock) return;
    setIsKnocking(true);
    setTimeout(() => setIsKnocking(false), 800);
    onKnock();
  };

  const haloColor = HALO_COLORS[colorPalette] || HALO_COLORS.blue_grey;

  return (
    <div
      className={`threshold-door-wrapper ${isIntro ? 'clickable' : ''} ${isKnocking ? 'knocking' : ''}`}
      onClick={handleClick}
      style={{ '--halo-color': haloColor, '--halo-opacity': haloOpacity }}
    >
      <svg
        className="door-svg"
        viewBox="0 0 200 320"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Outer glow / halo */}
        <defs>
          <filter id="doorGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="12" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <radialGradient id="lightGrad" cx="50%" cy="0%" r="100%">
            <stop offset="0%" stopColor={haloColor} stopOpacity={haloOpacity} />
            <stop offset="100%" stopColor={haloColor} stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Light emanating from behind door */}
        <ellipse cx="100" cy="50" rx="90" ry="200" fill="url(#lightGrad)" />

        {/* Door frame */}
        <rect x="20" y="20" width="160" height="280" rx="4" ry="4"
          fill="#1a1008" stroke="#3d2d1a" strokeWidth="6" />

        {/* Door panel — rotates on Y-axis (simulated with skew) */}
        <g
          style={{
            transform: `perspective(400px) rotateY(${currentAngle}deg)`,
            transformOrigin: '20px 160px',
            transition: 'none',
          }}
        >
          <rect x="20" y="20" width="160" height="280" rx="4"
            fill="#2a1a0a" stroke="#5c3d1a" strokeWidth="4" />

          {/* Door panels detail */}
          <rect x="35" y="40" width="130" height="110" rx="3"
            fill="none" stroke="#4a2e10" strokeWidth="2" opacity="0.7" />
          <rect x="35" y="165" width="130" height="110" rx="3"
            fill="none" stroke="#4a2e10" strokeWidth="2" opacity="0.7" />

          {/* Door knob */}
          <circle cx="155" cy="165" r="8" fill="#8B6914" />
          <circle cx="155" cy="165" r="5" fill="#c49a1e" />

          {/* Keyhole */}
          <circle cx="155" cy="180" r="3" fill="#1a0e00" />
          <rect x="153" y="180" width="4" height="8" rx="1" fill="#1a0e00" />
        </g>

        {/* Frame molding */}
        <rect x="14" y="14" width="172" height="292" rx="6"
          fill="none" stroke="#5c4020" strokeWidth="8" />
        <rect x="10" y="10" width="180" height="300" rx="8"
          fill="none" stroke="#3d2810" strokeWidth="4" />

        {/* Ground shadow */}
        <ellipse cx="100" cy="305" rx="85" ry="8"
          fill="#000" opacity="0.4" />
      </svg>

      {/* Knocker animation circles */}
      {isKnocking && (
        <div className="knock-ripples">
          {[1, 2, 3].map((i) => (
            <div key={i} className="knock-ripple" style={{ animationDelay: `${i * 0.12}s` }} />
          ))}
        </div>
      )}

      {isIntro && !isLoading && (
        <p className="door-prompt">knock to enter</p>
      )}
      {isLoading && (
        <p className="door-prompt loading-dots">opening<span>.</span><span>.</span><span>.</span></p>
      )}
    </div>
  );
}
