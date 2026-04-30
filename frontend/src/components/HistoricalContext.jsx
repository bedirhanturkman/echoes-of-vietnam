/**
 * HistoricalContext — The Echoing Threshold
 * Floating right-side panel showing Gemini-generated historical notes.
 */
import { useState, useEffect } from 'react';

export default function HistoricalContext({ note, musicParams }) {
  const [visible, setVisible] = useState(false);
  const [currentNote, setCurrentNote] = useState(null);

  useEffect(() => {
    if (note) {
      setVisible(false);
      setTimeout(() => {
        setCurrentNote(note);
        setVisible(true);
      }, 400);
    }
  }, [note]);

  return (
    <aside className={`historical-panel ${visible && currentNote ? 'visible' : ''}`}>
      <div className="hist-inner">
        <div className="hist-badge">
          <span className="hist-year">{currentNote?.year ?? '1973'}</span>
          <span className="hist-divider">—</span>
          <span className="hist-label">Historical Context</span>
        </div>

        {currentNote ? (
          <>
            <p className="hist-event">{currentNote.event}</p>
            <p className="hist-connection">{currentNote.connection}</p>
          </>
        ) : (
          <p className="hist-event placeholder">
            "The times they are a-changin'..."
          </p>
        )}

        <div className="music-info">
          <div className="music-info-row">
            <span className="music-label">Key</span>
            <span className="music-value">{musicParams.key}</span>
          </div>
          <div className="music-info-row">
            <span className="music-label">Tempo</span>
            <span className="music-value">{musicParams.tempo_bpm} BPM</span>
          </div>
          <div className="music-info-row">
            <span className="music-label">Layer</span>
            <span className="music-value">{musicParams.instrument_layer}</span>
          </div>
          <div className="music-info-row">
            <span className="music-label">Soundscape</span>
            <span className="music-value">
              {musicParams.historical_soundscape?.replace('_', ' ')}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
