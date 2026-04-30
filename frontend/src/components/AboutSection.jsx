import { BrainCircuit, Database, DoorOpen, Map, Music } from 'lucide-react';

export default function AboutSection() {
  return (
    <section className="about-section animate-fade-in">
      <h2>Technical Concept</h2>
      <p style={{ maxWidth: '1000px' }}>
        Echoes Through the Door is an AI memory-to-melody archive. The user gives only a
        historical starting point: a date range, region, or a single Knock. The system selects
        historical events, infers emotion and themes, maps them into a semantic memory space, and
        generates a deterministic 1970s folk-inspired MIDI composition.
      </p>

      <div className="pipeline-diagram">
        <div className="pipeline-node">
          <DoorOpen size={32} style={{ color: 'var(--accent)', marginBottom: '10px' }} />
          <div>Threshold Query</div>
        </div>
        <div className="pipeline-arrow">-&gt;</div>
        <div className="pipeline-node">
          <Database size={32} style={{ color: 'var(--muted)', marginBottom: '10px' }} />
          <div>Historical Archive</div>
        </div>
        <div className="pipeline-arrow">-&gt;</div>
        <div className="pipeline-node">
          <BrainCircuit size={32} style={{ color: 'var(--blue-muted)', marginBottom: '10px' }} />
          <div>AI/NLP Analysis</div>
        </div>
        <div className="pipeline-arrow">-&gt;</div>
        <div className="pipeline-node">
          <Map size={32} style={{ color: 'var(--peace)', marginBottom: '10px' }} />
          <div>Theme Similarity</div>
        </div>
        <div className="pipeline-arrow">-&gt;</div>
        <div className="pipeline-node">
          <Music size={32} style={{ color: 'var(--text)', marginBottom: '10px' }} />
          <div>MIDI Melody</div>
        </div>
      </div>
    </section>
  );
}
