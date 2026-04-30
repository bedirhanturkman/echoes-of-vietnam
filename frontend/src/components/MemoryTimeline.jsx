import { getCategoryColor } from '../utils/musicGeneration';

const sortedEvents = (events) =>
  [...events].sort((a, b) => String(a.date).localeCompare(String(b.date)));

export default function MemoryTimeline({ events, selectedEvent, activePreviewEventId, onSelectEvent }) {
  return (
    <div className="panel-card memory-timeline">
      <h3>Memory Timeline</h3>
      <div className="timeline-track">
        {sortedEvents(events).map((event) => {
          const isActive = selectedEvent?.id === event.id || activePreviewEventId === event.id;

          return (
            <button
              key={event.id}
              type="button"
              className={`timeline-item ${isActive ? 'active' : ''} ${activePreviewEventId === event.id ? 'preview-active' : ''}`}
              onClick={() => onSelectEvent(event)}
              style={{ '--item-color': getCategoryColor(event.category) }}
            >
              <span className="timeline-dot" />
              <span className="timeline-date">{event.date}</span>
              <span className="timeline-title">{event.title}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
