import { useState } from 'react';
import EmbeddingMap from './EmbeddingMap';
import SoundscapePlayer from './SoundscapePlayer';
import InterpretationPanel from './InterpretationPanel';
import MemoryTimeline from './MemoryTimeline';
import NoteSequence from './NoteSequence';

export default function ResultSection({
  result,
  melody,
  selectedMood,
  onMoodChange,
  previewTime,
  isPreviewing,
  activePreviewEventId,
  onPreviewToggle,
  onPreviewReset,
}) {
  const [selectedEvent, setSelectedEvent] = useState(null);

  const events = result?.events || [];
  const musicMetadata = result?.musicMetadata || result?.music_metadata || {};
  const interpretationText = result?.interpretationText || result?.interpretation_text || "";
  const previewEvent = events.find((event) => event.id === activePreviewEventId);
  const displayedSelectedEvent = previewEvent || selectedEvent;

  return (
    <section className="result-section animate-fade-in" id="result-section">
      <div className="result-grid">
        <EmbeddingMap 
          data={events} 
          selectedEvent={displayedSelectedEvent}
          activePreviewEventId={activePreviewEventId}
          onSelectEvent={setSelectedEvent}
        />
        <SoundscapePlayer
          melody={melody}
          musicMetadata={musicMetadata}
          selectedMood={selectedMood}
          onMoodChange={onMoodChange}
          isPreviewing={isPreviewing}
          onPreviewToggle={onPreviewToggle}
          onPreviewReset={onPreviewReset}
        />
      </div>
      <MemoryTimeline
        events={events}
        selectedEvent={displayedSelectedEvent}
        activePreviewEventId={activePreviewEventId}
        onSelectEvent={setSelectedEvent}
      />
      <NoteSequence
        melody={melody}
        events={events}
        selectedEvent={displayedSelectedEvent}
        activePreviewEventId={activePreviewEventId}
        previewTime={previewTime}
        isPreviewing={isPreviewing}
        onSelectEvent={setSelectedEvent}
      />
      <div className="panel-card generation-explainer">
        <h3>How the composition is generated</h3>
        <p>
          Each historical event contributes to the composition. Semantic/category clusters choose
          harmonic sections, mood selects scale and tempo, event coordinates influence pitch and
          velocity, and intensity shapes duration. The final MIDI combines melody, bass, and chord
          layers.
        </p>
      </div>
      <InterpretationPanel text={interpretationText} selectedEvent={displayedSelectedEvent} />
    </section>
  );
}
