import React, { useState } from 'react';
import { Play, Pause, Download } from 'lucide-react';

export default function SoundscapePlayer() {
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => setIsPlaying(!isPlaying);

  return (
    <div className="panel-card">
      <h3>Generated Soundscape</h3>
      
      <div className="player-controls">
        <button className="play-btn" onClick={togglePlay}>
          {isPlaying ? <Pause size={24} /> : <Play size={24} style={{ marginLeft: '4px' }} />}
        </button>
        <div className={`waveform ${isPlaying ? 'playing' : ''}`}>
          {Array.from({ length: 24 }).map((_, i) => (
            <div 
              key={i} 
              className="bar" 
              style={{ animationDelay: `${i * 0.05}s` }}
            />
          ))}
        </div>
      </div>

      <div className="music-stats">
        <div className="stat-box">
          <div className="stat-value">72 BPM</div>
          <div className="stat-label">Tempo</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">A min pent.</div>
          <div className="stat-label">Scale</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">G - D - Am7</div>
          <div className="stat-label">Progression</div>
        </div>
        <div className="stat-box">
          <div className="stat-value" style={{ color: 'var(--muted)' }}>Tired / Accepting</div>
          <div className="stat-label">Mood</div>
        </div>
      </div>

      <div className="download-buttons">
        <button className="secondary-btn" title="Coming soon" disabled>
          <Download size={16} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          MIDI
        </button>
        <button className="secondary-btn" title="Coming soon" disabled>
          <Download size={16} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          WAV
        </button>
      </div>
    </div>
  );
}
