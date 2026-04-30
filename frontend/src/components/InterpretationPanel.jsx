export default function InterpretationPanel({ text, selectedEvent }) {
  const globalText = text ||
    "\u201CBu kompozisyon Vietnam Savaşı'na ait verilerden üretilmiştir. Haritadaki noktalar notalara, acılar ve barışlar melodinin ritmine dönüşüyor.\u201D";

  return (
    <div className="interpretation-panel">
      <div className="global-interpretation">
        <h3>Musical Interpretation</h3>
        <p>&ldquo;{globalText}&rdquo;</p>
      </div>

      {selectedEvent && (
        <div className="event-interpretation" style={{ marginTop: '20px', padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', borderLeft: '3px solid #ff4d4d' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#ff4d4d' }}>{selectedEvent.title} ({selectedEvent.date})</h4>
          <p style={{ fontStyle: 'italic', margin: 0 }}>&ldquo;{selectedEvent.musicalInterpretation}&rdquo;</p>
        </div>
      )}
    </div>
  );
}
