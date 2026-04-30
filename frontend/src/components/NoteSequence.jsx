import { getCategoryColor } from '../utils/musicGeneration';

const ROLE_HEIGHT = {
  melody: 14,
  chord: 10,
  bass: 12,
  harmony: 9,
  beat: 11,
};

export default function NoteSequence({
  melody,
  selectedEvent,
  activePreviewEventId,
  previewTime = 0,
  isPreviewing,
  onSelectEvent,
  events,
}) {
  const safeMelody = melody || [];
  const eventById = new Map(events.map((event) => [event.id, event]));
  const duration = safeMelody.reduce(
    (latest, note) => Math.max(latest, note.startTime + note.duration),
    1
  );
  const minPitch = Math.min(...safeMelody.map((note) => note.pitch), 36);
  const maxPitch = Math.max(...safeMelody.map((note) => note.pitch), 96);
  const pitchRange = Math.max(1, maxPitch - minPitch);

  return (
    <div className="panel-card note-sequence">
      <h3>Generated Note Sequence</h3>
      <p className="silent-preview-label">Silent visual preview - download MIDI to listen.</p>
      <div className="note-lane">
        <div
          className={`preview-playhead ${isPreviewing ? 'active' : ''}`}
          style={{ left: `${Math.min(100, Math.max(0, (previewTime / duration) * 100))}%` }}
        />
        {safeMelody.map((note, index) => {
          const event = eventById.get(note.eventId);
          const left = (note.startTime / duration) * 100;
          const width = Math.max(0.8, (note.duration / duration) * 100);
          const bottom = ((note.pitch - minPitch) / pitchRange) * 82 + 6;
          const isActiveNote =
            note.startTime <= previewTime && previewTime <= note.startTime + note.duration;
          const isRelatedEvent =
            selectedEvent?.id === note.eventId || activePreviewEventId === note.eventId;

          return (
            <button
              key={note.id || `${note.eventId}-${index}`}
              type="button"
              className={`note-bar ${note.role} ${isRelatedEvent ? 'active' : ''} ${isActiveNote ? 'preview-active' : ''}`}
              style={{
                left: `${left}%`,
                width: `${width}%`,
                bottom: `${bottom}%`,
                height: ROLE_HEIGHT[note.role] || 10,
                '--note-color': getCategoryColor(note.category),
              }}
              onClick={() => event && onSelectEvent(event)}
              title={`${note.role} ${note.pitch} ${event?.title || ''}`}
            />
          );
        })}
      </div>
    </div>
  );
}
