import { ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const CATEGORY_COLORS = {
  conflict: '#8f3f32',         // danger
  peace_talks: '#7c9c72',      // peace
  civilian_impact: '#a89c8a',  // muted
  political_transition: '#c58b45', // accent
  uncertainty: '#6f8796'       // blue-muted
};

function CustomTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div style={{ backgroundColor: 'var(--panel-soft)', padding: '10px', border: '1px solid var(--muted)', borderRadius: '4px' }}>
        <p style={{ color: 'var(--text)', margin: 0, fontWeight: 500 }}>{data.title}</p>
        <p style={{ color: 'var(--muted)', margin: 0, fontSize: '0.8rem' }}>{data.date}</p>
      </div>
    );
  }
  return null;
}

export default function EmbeddingMap({ data, selectedEvent, activePreviewEventId, onSelectEvent }) {
  return (
    <div className="panel-card">
      <h3>Historical Embedding Map</h3>
      <p style={{ fontSize: '0.9rem', color: 'var(--muted)', marginBottom: '1rem' }}>
        2D Semantic projection of historical fragments. Click a node to inspect.
      </p>
      
      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
            <XAxis type="number" dataKey="x" name="X" hide />
            <YAxis type="number" dataKey="y" name="Y" hide />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
            <Scatter 
              name="Events" 
              data={data} 
              onClick={(e) => onSelectEvent(e.payload || e)}
            >
              {data.map((entry, index) => {
                const isSelected = selectedEvent?.id === entry.id;
                const isPreviewActive = activePreviewEventId === entry.id;

                return (
                  <Cell
                    key={`cell-${index}`}
                    fill={CATEGORY_COLORS[entry.category] || '#ffffff'}
                    cursor="pointer"
                    style={{
                      filter: isPreviewActive ? 'drop-shadow(0 0 8px var(--accent))' : 'none',
                      transition: 'all 0.3s',
                    }}
                    r={isSelected || isPreviewActive ? 9 : 5}
                    stroke={isSelected || isPreviewActive ? 'var(--text)' : 'none'}
                    strokeWidth={isPreviewActive ? 3 : 2}
                  />
                );
              })}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {selectedEvent && (
        <div className="detail-card animate-fade-in">
          <h4>{selectedEvent.title}</h4>
          <div className="detail-item">
            <span className="detail-label">Date:</span>
            <span className="detail-value">{selectedEvent.date}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Category:</span>
            <span className="detail-value">{selectedEvent.category.replace('_', ' ')}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Sentiment:</span>
            <span className="detail-value">{selectedEvent.sentiment}</span>
          </div>
          <div className="detail-item" style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px dashed var(--muted)'}}>
            <span className="detail-label">Sound:</span>
            <span className="detail-value" style={{ fontStyle: 'italic', color: 'var(--accent)' }}>
              "{selectedEvent.musicalInterpretation}"
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
