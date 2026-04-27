import React, { useState } from 'react';
import { Play, Pause, Download } from 'lucide-react';

export default function SoundscapePlayer({ musicMetadata, midiUrl }) {
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => setIsPlaying(!isPlaying);

  const tempo = musicMetadata?.tempo_bpm || 72;
  const scale = musicMetadata?.scale_name || "Pentatonic";
  const chords = musicMetadata?.chord_progression || "G - D - Am7";
  const mood = musicMetadata?.mood || "uncertain";
  const totalNotes = musicMetadata?.total_notes || 0;
  const durationSec = musicMetadata?.duration_seconds || 0;

  const handleDownloadMidi = () => {
    if (midiUrl) {
      const link = document.createElement('a');
      link.href = midiUrl;
      link.download = midiUrl.split('/').pop();
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

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
          <div className="stat-value">{tempo} BPM</div>
          <div className="stat-label">Tempo</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{scale}</div>
          <div className="stat-label">Scale</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{chords}</div>
          <div className="stat-label">Progression</div>
        </div>
        <div className="stat-box">
          <div className="stat-value" style={{ color: 'var(--muted)' }}>{mood}</div>
          <div className="stat-label">Mood</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{totalNotes}</div>
          <div className="stat-label">Notes</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{durationSec}s</div>
          <div className="stat-label">Duration</div>
        </div>
      </div>

      <div className="download-buttons">
        <button 
          className="secondary-btn" 
          onClick={handleDownloadMidi}
          disabled={!midiUrl}
          style={midiUrl ? { opacity: 1, cursor: 'pointer' } : {}}
        >
          <Download size={16} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          Download MIDI
        </button>
      </div>
    </div>
  );
}
