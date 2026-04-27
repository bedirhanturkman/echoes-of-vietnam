import React, { useState } from 'react';
import EmbeddingMap from './EmbeddingMap';
import SoundscapePlayer from './SoundscapePlayer';
import InterpretationPanel from './InterpretationPanel';
import { mockEvents } from '../data/mockEvents';

export default function ResultSection() {
  const [selectedEvent, setSelectedEvent] = useState(null);

  return (
    <section className="result-section animate-fade-in" id="result-section">
      <div className="result-grid">
        <EmbeddingMap 
          data={mockEvents} 
          selectedEvent={selectedEvent}
          onSelectEvent={setSelectedEvent}
        />
        <SoundscapePlayer />
      </div>
      <InterpretationPanel />
    </section>
  );
}
