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
  const midiUrl = result?.midiUrl || result?.midi_url || null;
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
          midiUrl={midiUrl}
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
      <div className="panel-card analysis-grid-card">
        <h3>AI Historical-Emotional Analysis</h3>
        <div className="analysis-grid">
          {events.map((event) => (
            <button
              className={`analysis-card ${displayedSelectedEvent?.id === event.id ? 'active' : ''}`}
              key={event.id}
              onClick={() => setSelectedEvent(event)}
            >
              <span className="analysis-date">{event.date}</span>
              <strong>{event.title}</strong>
              <span>{event.dominantEmotion || 'interpreted memory'}</span>
              <span className="analysis-themes">{(event.themes || []).join(' / ')}</span>
              <p>{event.aiSummary || event.musicalInterpretation}</p>
              {event.musicalMapping && (
                <small>
                  {event.musicalMapping.scale} -&gt; {event.musicalMapping.chord} -&gt; {event.musicalMapping.motif}
                </small>
              )}
            </button>
          ))}
        </div>
      </div>
      <div className="panel-card generation-explainer">
        <h3>How the composition is generated</h3>
        <p>
          Each historical event contributes a motif. AI/NLP analysis estimates dominant emotion,
          themes, intensity, and historical weight. Theme similarity maps the event toward farewell,
          mortality, war, hope, guilt, transition, and legacy. The music engine turns those values
          into scale, chord, pitch, velocity, rhythm, bass, beat, and harmony layers.
        </p>
        <p>
          {musicMetadata?.folkInspiration ||
            "Rather than copying Bob Dylan's melodies, the system models broad 1970s folk harmony principles: simple I-IV-V progressions, acoustic phrasing, descending farewell motifs, and unresolved transitions."}
        </p>
      </div>
      <InterpretationPanel text={interpretationText} selectedEvent={displayedSelectedEvent} />
    </section>
  );
}
