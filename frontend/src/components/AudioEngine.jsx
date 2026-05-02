/**
 * AudioEngine.jsx — The Echoing Threshold
 * Advanced Emotional Engine with 8 Distinct States.
 */
import React, { useState, useEffect, useRef } from 'react';
import '../AudioControl.css';

const CHORD_PROGRESSIONS = {
  G: [196.0, 246.9, 293.7, 392.0],
  D: [146.8, 185.0, 220.0, 293.7],
  Am: [220.0, 261.6, 329.6, 440.0],
  Em: [164.8, 196.0, 246.9, 329.6],
  C: [261.6, 329.6, 392.0, 523.3],
  F: [174.6, 220.0, 261.6, 349.2],
  B7: [123.5, 155.6, 196.0, 246.9],
  Dm: [146.8, 174.6, 220.0, 293.7],
  E: [164.8, 207.6, 246.9, 329.6],
};

const MOTIFS = {
  melancholy: ['G2', 'B2', 'D3', 'G3', 'F2', 'A2', 'C3', 'F3'],
  hope:       ['G5', 'A5', 'B5', 'D6', 'G6', 'D6', 'B5', 'G5'],
  resistance: ['E4', 'E4', 'G4', 'A4', 'B4', 'B4', 'A4', 'G4'],
  neutral:    ['G4', 'B4', 'D5', 'G5', 'D5', 'B4', 'G4', 'C5'],
  nostalgia:  ['C4', 'E4', 'G4', 'B4', 'A4', 'G4', 'E4', 'D4'],
  rage:       ['D4', 'D#4', 'D4', 'F4', 'E4', 'G4', 'F#4', 'A4'],
  peace:      ['G5', 'D6', 'B5', 'G6', 'D6', 'B5', 'G5', 'C6'],
  anxiety:    ['E3', 'Bb3', 'E4', 'Bb4', 'E3', 'Bb3', 'F3', 'B3'],
  fear:       ['C3', 'C3', 'Bb2', 'Ab2', 'G2', 'Ab2', 'C3', 'Eb3'],
  guilt:      ['A2', 'C3', 'E3', 'A3', 'G3', 'E3', 'C3', 'B2'],
  grief:      ['F2', 'Ab2', 'C3', 'Eb3', 'Db3', 'Bb2', 'Ab2', 'F2'],
  tenderness: ['C5', 'E5', 'G5', 'B5', 'A5', 'G5', 'E5', 'D5'],
  longing:    ['G3', 'B3', 'D4', 'F#4', 'E4', 'D4', 'B3', 'A3'],
  violence:   ['B3', 'B3', 'C4', 'B3', 'G3', 'F#3', 'E3', 'D3'],
  silence:    ['G4', 'G4', 'G4', 'F4', 'E4', 'E4', 'D4', 'D4'],
  confusion:  ['G4', 'Bb4', 'A4', 'C5', 'B4', 'G4', 'Ab4', 'F4'],
};

const PROGRESSIONS = {
  neutral:    ['G', 'D', 'Am', 'C'],
  melancholy: ['Am', 'Em', 'F', 'C'],
  hope:       ['G', 'C', 'D', 'G'],
  resistance: ['Em', 'B7', 'C', 'Am'],
  nostalgia:  ['C', 'F', 'G', 'C'],
  rage:       ['Dm', 'E', 'F', 'E'],
  peace:      ['G', 'C', 'G', 'D'],
  anxiety:    ['Em', 'B7', 'Em', 'B7'],
  fear:       ['Am', 'Dm', 'Am', 'E'],
  guilt:      ['Am', 'F', 'C', 'E'],
  grief:      ['Dm', 'Am', 'F', 'C'],
  tenderness: ['C', 'G', 'Am', 'F'],
  longing:    ['G', 'Em', 'C', 'D'],
  violence:   ['Dm', 'E', 'Dm', 'E'],
  silence:    ['G', 'D', 'G', 'D'],
  confusion:  ['Am', 'F', 'Dm', 'B7'],
};

export default function AudioEngine({ musicParams }) {
  const [status, setStatus] = useState('idle');
  const [isReady, setIsReady] = useState(false);
  
  const layersRef = useRef({ 
    ambient: null, piano: null, harm: null, 
    kick: null, snare: null, filter: null, distortion: null, reverb: null, seq: null 
  });
  
  const paramsRef = useRef(musicParams);
  useEffect(() => { paramsRef.current = musicParams; }, [musicParams]);

  const initAudio = async () => {
    if (status !== 'idle') return;
    const Tone = window.Tone;
    await Tone.start();
    setStatus('playing');

    const limiter = new Tone.Limiter(-1).toDestination();
    const compressor = new Tone.Compressor({ threshold: -24, ratio: 4 }).connect(limiter);
    const reverb = new Tone.Reverb({ decay: 6, wet: 0.3 }).connect(compressor);
    const filter = new Tone.Filter(3000, 'lowpass').connect(reverb);
    const distortion = new Tone.Distortion(0).connect(filter);

    const ambient = new Tone.PolySynth(Tone.Synth, {
      maxPolyphony: 32, oscillator: { type: 'sine' }, envelope: { attack: 2, release: 2 }, volume: -12
    }).connect(distortion);

    const piano = new Tone.PolySynth(Tone.Synth, {
      maxPolyphony: 32, oscillator: { type: 'triangle' }, envelope: { attack: 0.01, release: 1 }, volume: -60
    }).connect(distortion);

    const harm = new Tone.PolySynth(Tone.Synth, {
      maxPolyphony: 32, oscillator: { type: 'square' }, envelope: { attack: 0.2, release: 0.5 }, volume: -60
    }).connect(distortion);

    const kick = new Tone.MembraneSynth({ volume: -4 }).connect(compressor);
    const snare = new Tone.NoiseSynth({ volume: -18, envelope: { decay: 0.08 } }).connect(compressor);

    layersRef.current = { ambient, piano, harm, kick, snare, filter, distortion, reverb };

    let step = 0;
    const seq = new Tone.Sequence((time) => {
      const p = paramsRef.current;
      const progType = p.chord_progression_type || 'neutral';
      const prog = PROGRESSIONS[progType] || PROGRESSIONS.neutral;
      const motif = MOTIFS[progType] || MOTIFS.neutral;
      const Tone = window.Tone;

      // 1. Chords
      if (step % 8 === 0) {
        const chord = prog[Math.floor(step / 8) % prog.length];
        const freqs = CHORD_PROGRESSIONS[chord] || CHORD_PROGRESSIONS.G;
        freqs.forEach((f, i) => ambient.triggerAttackRelease(Tone.Frequency(f, 'hz').toNote(), '2n', time, 0.4));
      }

      // 2. Rhythm
      if (progType === 'resistance' || progType === 'rage') {
        if (step % 2 === 0) kick.triggerAttackRelease("C1", "16n", time);
        if (step % 4 === 3) snare.triggerAttackRelease("32n", time, 0.2);
      } else if (progType === 'anxiety') {
        if (step % 3 === 0) kick.triggerAttackRelease("C1", "16n", time, 0.3); // Odd timing
      } else {
        if (step % 8 === 0) kick.triggerAttackRelease("C1", "8n", time, 0.4);
      }

      // 3. Motif
      const melodyNote = motif[step % motif.length];
      if (p.instrument_layer === 'piano') {
        piano.triggerAttackRelease(melodyNote, '8n', time, 0.7);
      } else if (p.instrument_layer === 'harmonika') {
        harm.triggerAttackRelease(melodyNote, '8n', time, 0.5);
      }

      step++;
    }, [0, 1, 2, 3, 4, 5, 6, 7], "16n");

    layersRef.current.seq = seq;
    seq.start(0);
    Tone.Transport.start();
    setIsReady(true);
  };

  const toggleMute = () => {
    const Tone = window.Tone;
    if (status === 'playing') {
      Tone.Transport.pause();
      setStatus('muted');
    } else {
      Tone.Transport.start();
      setStatus('playing');
    }
  };

  useEffect(() => {
    if (!isReady) return;
    const Tone = window.Tone;
    const p = musicParams;
    const l = layersRef.current;
    const t = p.chord_progression_type;

    // Use cross_fade_seconds from params as the ramp duration, clamped shorter for sharpness
    const ramp = Math.min(p.cross_fade_seconds ?? 1.5, 0.6);

    Tone.Transport.bpm.rampTo(p.tempo_bpm, ramp);

    // Per-emotion filter cutoff — wide spread for distinct tonal color
    const CUTOFF = {
      melancholy: 400,  grief: 350,    guilt: 450,
      nostalgia:  600,  longing: 700,  tenderness: 2000,
      neutral:    2500, silence: 1200, confusion: 1800,
      hope:       5000, peace: 7000,
      anxiety:    3500, fear: 2800,
      resistance: 4000, rage: 4500,    violence: 5000,
    };
    l.filter.frequency.rampTo(CUTOFF[t] ?? 2500, ramp);

    // Distortion — aggressive only for violent/rage/resistance
    const DISTORTION = {
      rage: 0.6, violence: 0.55, resistance: 0.4, fear: 0.2, anxiety: 0.15,
    };
    l.distortion.distortion = DISTORTION[t] ?? 0;

    // Reverb — heavy for introspective, dry for raw/violent
    const REVERB = {
      peace: 0.85, melancholy: 0.8, grief: 0.75, silence: 0.9,
      tenderness: 0.6, nostalgia: 0.65, longing: 0.7, guilt: 0.7,
      neutral: 0.4, confusion: 0.5,
      hope: 0.35, resistance: 0.25, anxiety: 0.3, fear: 0.3,
      rage: 0.15, violence: 0.1,
    };
    l.reverb.wet.rampTo(REVERB[t] ?? 0.35, ramp);

    l.piano.volume.rampTo(p.instrument_layer === 'piano' ? -5 : -60, ramp);
    l.harm.volume.rampTo(p.instrument_layer === 'harmonika' ? -5 : -60, ramp);
  }, [musicParams, isReady]);

  return (
    <div className="audio-control-panel">
      {status === 'idle' ? (
        <button className="audio-toggle-btn" onClick={initAudio}>
          <div className="icon-box">♪</div>
          <div className="label-box">ENTER SOUNDSCAPE</div>
        </button>
      ) : (
        <button className="audio-toggle-btn" onClick={toggleMute}>
          <div className="icon-box">{status === 'playing' ? '❙❙' : '▶'}</div>
          <div className="label-box">{musicParams.chord_progression_type?.toUpperCase()}</div>
          {status === 'playing' && (
            <div className="audio-visualizer">
              {[...Array(4)].map((_, i) => <div key={i} className="vis-bar" />)}
            </div>
          )}
        </button>
      )}
    </div>
  );
}
