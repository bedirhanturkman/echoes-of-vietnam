/**
 * AtmosphereCanvas — The Echoing Threshold
 * Renders the dynamic animated background: clouds, particles, color shifts.
 * Driven by visualParams from the emotion pipeline.
 */
import { useEffect, useRef } from 'react';

const PALETTES = {
  blue_grey: {
    sky1: '#0d1b2a',
    sky2: '#1b2d44',
    cloudColor: 'rgba(100, 130, 160, ',
    accent: '#4a7fa5',
  },
  warm_amber: {
    sky1: '#1a0f00',
    sky2: '#3d1f00',
    cloudColor: 'rgba(210, 140, 60, ',
    accent: '#e8854a',
  },
  stormy_dark: {
    sky1: '#050810',
    sky2: '#0e1520',
    cloudColor: 'rgba(60, 70, 90, ',
    accent: '#2a3a5c',
  },
  golden_dusk: {
    sky1: '#1a0e00',
    sky2: '#2e1a00',
    cloudColor: 'rgba(220, 160, 80, ',
    accent: '#d4a044',
  },
  deep_red: {
    sky1: '#1a0505',
    sky2: '#3d0a0a',
    cloudColor: 'rgba(120, 20, 20, ',
    accent: '#ff0000',
  },
  ethereal_white: {
    sky1: '#0f172a',
    sky2: '#1e293b',
    cloudColor: 'rgba(200, 220, 255, ',
    accent: '#38bdf8',
  },
  sickly_green: {
    sky1: '#051a05',
    sky2: '#1a2e1a',
    cloudColor: 'rgba(80, 120, 80, ',
    accent: '#adff2f',
  },
  sepia_glow: {
    sky1: '#1c140d',
    sky2: '#3d2b1f',
    cloudColor: 'rgba(150, 110, 80, ',
    accent: '#d4a373',
  },
};

export default function AtmosphereCanvas({ visualParams }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const stateRef = useRef({
    clouds: [],
    particles: [],
    time: 0,
    currentPalette: PALETTES.blue_grey,
    targetPalette: PALETTES.blue_grey,
    lerpT: 1,
    cloudDensity: 0.4,
    particleIntensity: 0.1,
  });

  // Update target state when props change
  useEffect(() => {
    const s = stateRef.current;
    s.targetPalette = PALETTES[visualParams.color_palette] || PALETTES.blue_grey;
    s.cloudDensity = visualParams.cloud_density;
    s.particleIntensity = visualParams.particle_intensity;
    s.lerpT = 0; // Start transition
  }, [visualParams]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initClouds(stateRef.current, canvas);
    };

    window.addEventListener('resize', resize);
    resize();

    const loop = () => {
      const s = stateRef.current;
      s.time += 0.003;

      // Lerp palette
      if (s.lerpT < 1) {
        s.lerpT = Math.min(1, s.lerpT + 0.008);
        s.currentPalette = lerpPalette(s.currentPalette, s.targetPalette, s.lerpT);
      }

      draw(ctx, canvas, s);
      animRef.current = requestAnimationFrame(loop);
    };

    animRef.current = requestAnimationFrame(loop);
    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
      }}
    />
  );
}

// ─── Initialization ──────────────────────────────────────────────

function initClouds(s, canvas) {
  s.clouds = Array.from({ length: 12 }, (_, i) => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height * 0.6,
    w: 120 + Math.random() * 300,
    h: 40 + Math.random() * 80,
    speed: 0.1 + Math.random() * 0.25,
    alpha: 0.1 + Math.random() * 0.4,
    layer: i % 3,
  }));
  s.particles = Array.from({ length: 40 }, () => createParticle(canvas));
}

function createParticle(canvas) {
  return {
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * 0.2,
    vy: -0.1 - Math.random() * 0.3,
    size: 0.5 + Math.random() * 1.5,
    alpha: Math.random() * 0.4,
    life: Math.random(),
  };
}

// ─── Drawing ─────────────────────────────────────────────────────

function draw(ctx, canvas, s) {
  const { w, h } = { w: canvas.width, h: canvas.height };
  const pal = s.currentPalette;

  // Sky gradient
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, pal.sky1);
  grad.addColorStop(1, pal.sky2);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);

  // Clouds
  const targetClouds = Math.floor(s.cloudDensity * 12);
  s.clouds.forEach((c, i) => {
    c.x += c.speed * (0.5 + (c.layer * 0.3));
    if (c.x - c.w > w) c.x = -c.w;

    const visible = i < targetClouds;
    const alpha = visible ? c.alpha * s.cloudDensity : 0;
    if (alpha < 0.01) return;

    ctx.save();
    ctx.filter = 'blur(18px)';
    ctx.fillStyle = `${pal.cloudColor}${alpha.toFixed(2)})`;
    ctx.beginPath();
    ctx.ellipse(c.x, c.y, c.w / 2, c.h / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  });

  // Accent glow (bottom horizon)
  const horizGrad = ctx.createLinearGradient(0, h * 0.6, 0, h);
  horizGrad.addColorStop(0, 'transparent');
  horizGrad.addColorStop(1, pal.accent + '22');
  ctx.fillStyle = horizGrad;
  ctx.fillRect(0, h * 0.6, w, h * 0.4);

  // Particles (floating dust / stars)
  s.particles.forEach((p) => {
    p.x += p.vx + Math.sin(s.time + p.y * 0.01) * 0.1;
    p.y += p.vy;
    p.life -= 0.003;
    if (p.life <= 0 || p.y < 0) Object.assign(p, createParticle(canvas));

    const maxAlpha = s.particleIntensity * 0.7;
    ctx.save();
    ctx.globalAlpha = p.alpha * p.life * maxAlpha;
    ctx.fillStyle = pal.accent;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  });
}

// ─── Helpers ─────────────────────────────────────────────────────

function lerpPalette(a, b, t) {
  return {
    sky1: a.sky1,     // Colors lerp via CSS transition in the DOM
    sky2: a.sky2,
    cloudColor: t > 0.5 ? b.cloudColor : a.cloudColor,
    accent: t > 0.5 ? b.accent : a.accent,
  };
}
