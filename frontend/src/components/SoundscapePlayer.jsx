import { Download } from 'lucide-react';
import MoodSelector from './MoodSelector';

export default function SoundscapePlayer({
  melody = null,
  musicMetadata,
  selectedMood,
  onMoodChange,
  midiUrl,
  isPreviewing,
  onPreviewToggle,
  onPreviewReset,
}) {
  const safeMelody = melody ?? [];
  const durationSec = safeMelody.reduce(
    (latest, note) => Math.max(latest, note.startTime + note.duration),
    0
  );
  const totalNotes = safeMelody.length;

  const handleDownloadMidi = () => {
    if (!midiUrl) return;
    window.location.href = midiUrl;
  };

  return (
    <div className="panel-card">
      <h3>Generated Soundscape</h3>
      <MoodSelector selectedMood={selectedMood} onMoodChange={onMoodChange} />
      
      <div className="player-controls decorative">
        <div className="waveform">
          {Array.from({ length: 24 }).map((_, i) => (
            <div 
              key={i} 
              className="bar" 
              style={{ height: `${18 + ((i * 17) % 70)}%` }}
            />
          ))}
        </div>
      </div>
      <p className="silent-preview-label">Silent visual preview - download MIDI to listen.</p>

      <div className="music-stats">
        <div className="stat-box">
          <div className="stat-value">{musicMetadata?.tempo_bpm || 0} BPM</div>
          <div className="stat-label">Tempo</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{musicMetadata?.scale_name || "Pentatonic"}</div>
          <div className="stat-label">Scale</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{musicMetadata?.chord_progression || "Generated"}</div>
          <div className="stat-label">Progression</div>
        </div>
        <div className="stat-box">
          <div className="stat-value" style={{ color: 'var(--muted)' }}>{musicMetadata?.mood || "data-driven"}</div>
          <div className="stat-label">Mood</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{totalNotes}</div>
          <div className="stat-label">Notes</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{durationSec.toFixed(1)}s</div>
          <div className="stat-label">Duration</div>
        </div>
      </div>

      <div className="download-buttons">
        <button
          className="secondary-btn"
          onClick={onPreviewToggle}
          disabled={!safeMelody.length || !midiUrl}
          style={safeMelody.length && midiUrl ? { opacity: 1, cursor: 'pointer' } : {}}
        >
          {isPreviewing ? "Stop Preview" : "Preview Composition"}
        </button>
        <button
          className="secondary-btn"
          onClick={onPreviewReset}
          disabled={!safeMelody.length}
          style={safeMelody.length ? { opacity: 1, cursor: 'pointer' } : {}}
        >
          Reset Preview
        </button>
        <button 
          className="secondary-btn" 
          onClick={handleDownloadMidi}
          disabled={!safeMelody.length}
          style={safeMelody.length ? { opacity: 1, cursor: 'pointer' } : {}}
        >
          <Download size={16} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          Download MIDI
        </button>
      </div>
    </div>
  );
}
