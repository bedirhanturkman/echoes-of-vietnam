import React from 'react';
import { UploadCloud } from 'lucide-react';

export default function UploadSection({ onSampleSelect }) {
  return (
    <section className="upload-section animate-fade-in" id="upload-section">
      <div className="upload-card">
        <h2>Upload Historical Data</h2>
        <div className="drop-zone">
          <UploadCloud size={48} className="upload-icon" />
          <p>Drop a CSV/JSON file here or use the sample dataset</p>
        </div>
        <button className="secondary-btn" onClick={onSampleSelect}>
          Use Sample Dataset
        </button>
        <p className="small-text">Expected columns: date, title, location, category, sentiment, casualties</p>
      </div>
    </section>
  );
}
