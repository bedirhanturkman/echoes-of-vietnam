import React, { useState } from 'react';
import EmbeddingMap from './EmbeddingMap';
import SoundscapePlayer from './SoundscapePlayer';
import InterpretationPanel from './InterpretationPanel';

export default function ResultSection({ result }) {
  const [selectedEvent, setSelectedEvent] = useState(null);

  const events = result?.events || [];
  const musicMetadata = result?.music_metadata || {};
  const midiUrl = result?.midi_url || null;
  const interpretationText = result?.interpretation_text || "";

  return (
    <section className="result-section animate-fade-in" id="result-section">
      <div className="result-grid">
        <EmbeddingMap 
          data={events} 
          selectedEvent={selectedEvent}
          onSelectEvent={setSelectedEvent}
        />
        <SoundscapePlayer 
          musicMetadata={musicMetadata}
          midiUrl={midiUrl}
        />
      </div>
      <InterpretationPanel text={interpretationText} selectedEvent={selectedEvent} />
    </section>
  );
}
