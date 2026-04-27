import React from 'react';
import { Database, BrainCircuit, Map, Music, Headphones } from 'lucide-react';

export default function AboutSection() {
  return (
    <section className="about-section animate-fade-in">
      <h2>Technical Concept</h2>
      <p style={{ maxWidth: '1000px' }}>
        This prototype demonstrates a pipeline for conceptual data sonification. 
        It uses two main AI techniques: an <strong>OpenAI Embedding model</strong> to group 
        semantic concepts of historical records, and a <strong>Music/MIDI generation pipeline</strong> 
        to synthesize these spatial coordinates into a meaningful harmonic and rhythmic structure.
      </p>
      
      <div className="pipeline-diagram">
        <div className="pipeline-node">
          <Database size={32} style={{ color: 'var(--muted)', marginBottom: '10px' }} />
          <div>Historical Data</div>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-node">
          <BrainCircuit size={32} style={{ color: 'var(--blue-muted)', marginBottom: '10px' }} />
          <div>AI Embeddings</div>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-node">
          <Map size={32} style={{ color: 'var(--peace)', marginBottom: '10px' }} />
          <div>2D Memory Map</div>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-node">
          <Music size={32} style={{ color: 'var(--accent)', marginBottom: '10px' }} />
          <div>Musical Mapping Engine</div>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-node">
          <Headphones size={32} style={{ color: 'var(--text)', marginBottom: '10px' }} />
          <div>Audio Output</div>
        </div>
      </div>
    </section>
  );
}
