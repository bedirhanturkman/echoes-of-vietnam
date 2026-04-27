import React, { useRef, useState } from 'react';
import { UploadCloud } from 'lucide-react';

const API_BASE = '/api/v1/pipeline';

export default function UploadSection({ onPipelineStart }) {
  const [isUploading, setIsUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const startPipeline = async (file) => {
    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Upload failed');
      }

      const data = await response.json();
      onPipelineStart(data.task_id);
    } catch (err) {
      setError(err.message);
      setIsUploading(false);
    }
  };

  const handleSampleSelect = async () => {
    setIsUploading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/upload?use_sample=true`, {
        method: 'POST',
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to start sample pipeline');
      }

      const data = await response.json();
      onPipelineStart(data.task_id);
    } catch (err) {
      setError(err.message);
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) startPipeline(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) startPipeline(file);
  };

  return (
    <section className="upload-section animate-fade-in" id="upload-section">
      <div className="upload-card">
        <h2>Upload Historical Data</h2>
        <div
          className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          style={{ cursor: 'pointer' }}
        >
          <UploadCloud size={48} className="upload-icon" />
          <p>
            {isUploading
              ? 'Starting pipeline...'
              : 'Drop a CSV/JSON file here or click to browse'}
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.json"
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />
        </div>

        <button
          className="secondary-btn"
          onClick={handleSampleSelect}
          disabled={isUploading}
        >
          {isUploading ? 'Processing...' : 'Use Sample Dataset'}
        </button>

        {error && (
          <p style={{ color: 'var(--danger)', marginTop: '1rem', fontSize: '0.9rem' }}>
            ⚠️ {error}
          </p>
        )}

        <p className="small-text">
          Expected columns: date, title, location, category, sentiment, casualties
        </p>
      </div>
    </section>
  );
}
