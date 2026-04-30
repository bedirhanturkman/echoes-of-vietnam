import { useRef, useState } from 'react';
import { UploadCloud } from 'lucide-react';
import { mockEvents } from '../data/mockEvents';

const parseCsvLine = (line) => {
  const values = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    const nextChar = line[i + 1];

    if (char === '"' && nextChar === '"') {
      current += '"';
      i += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      values.push(current.trim());
      current = "";
    } else {
      current += char;
    }
  }

  values.push(current.trim());
  return values;
};

const parseCsv = (text) => {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  if (lines.length < 2) return [];

  const headers = parseCsvLine(lines[0]).map((header) => header.trim());
  return lines.slice(1).map((line, index) => {
    const values = parseCsvLine(line);
    const row = { id: `e${index + 1}` };
    headers.forEach((header, columnIndex) => {
      row[header] = values[columnIndex] ?? "";
    });
    return row;
  });
};

const parseDatasetFile = async (file) => {
  const text = await file.text();

  if (file.name.toLowerCase().endsWith(".json")) {
    const json = JSON.parse(text);
    if (Array.isArray(json)) return json;
    if (Array.isArray(json.events)) return json.events;
    throw new Error("JSON file must contain an array or an events array.");
  }

  return parseCsv(text);
};

export default function UploadSection({ onPipelineStart }) {
  const [isUploading, setIsUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const startPipeline = async (file) => {
    setIsUploading(true);
    setError(null);

    try {
      const events = await parseDatasetFile(file);
      if (!events.length) throw new Error("No events found in the selected file.");
      onPipelineStart(events);
    } catch (err) {
      setError(err.message);
      setIsUploading(false);
    }
  };

  const handleSampleSelect = async () => {
    setIsUploading(true);
    setError(null);
    onPipelineStart(mockEvents);
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
