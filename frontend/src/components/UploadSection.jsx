import { useState } from 'react';
import { CalendarRange, DoorOpen, MapPin } from 'lucide-react';

const THRESHOLDS = [
  { value: 'farewell', label: 'Farewell' },
  { value: 'war', label: 'War' },
  { value: 'hope', label: 'Hope' },
  { value: 'transition', label: 'Transition' },
  { value: 'legacy', label: 'Legacy' },
];

export default function UploadSection({ onPipelineStart }) {
  const [startYear, setStartYear] = useState(1968);
  const [endYear, setEndYear] = useState(1975);
  const [region, setRegion] = useState('Vietnam USA');
  const [threshold, setThreshold] = useState('farewell');
  const [error, setError] = useState(null);

  const startArchive = (knock = false) => {
    setError(null);
    const nextStart = knock ? 1968 : Number(startYear);
    const nextEnd = knock ? 1975 : Number(endYear);

    if (!Number.isFinite(nextStart) || !Number.isFinite(nextEnd) || nextStart > nextEnd) {
      setError('Please enter a valid year range.');
      return;
    }

    onPipelineStart({
      type: 'archive',
      knock,
      startYear: nextStart,
      endYear: nextEnd,
      region: knock ? 'Vietnam USA' : region,
      threshold: knock ? 'farewell' : threshold,
      label: knock
        ? 'Knock: 1968-1975 / Vietnam-USA / farewell'
        : `${nextStart}-${nextEnd} / ${region} / ${threshold}`,
    });
  };

  return (
    <section className="upload-section animate-fade-in" id="upload-section">
      <div className="upload-card archive-card">
        <h2>Open the Memory Archive</h2>
        <p className="archive-intro">
          Choose a date range, region, and threshold. The system selects historical fragments,
          analyzes their emotional weight, and turns them into a folk-inspired MIDI memory.
        </p>

        <div className="archive-form">
          <label className="archive-field">
            <span><CalendarRange size={16} /> Start year</span>
            <input
              type="number"
              value={startYear}
              min="1960"
              max="1980"
              onChange={(event) => setStartYear(event.target.value)}
            />
          </label>

          <label className="archive-field">
            <span><CalendarRange size={16} /> End year</span>
            <input
              type="number"
              value={endYear}
              min="1960"
              max="1980"
              onChange={(event) => setEndYear(event.target.value)}
            />
          </label>

          <label className="archive-field wide">
            <span><MapPin size={16} /> Region / country</span>
            <input
              type="text"
              value={region}
              onChange={(event) => setRegion(event.target.value)}
              placeholder="Vietnam USA"
            />
          </label>

          <label className="archive-field wide">
            <span><DoorOpen size={16} /> Threshold</span>
            <select value={threshold} onChange={(event) => setThreshold(event.target.value)}>
              {THRESHOLDS.map((item) => (
                <option value={item.value} key={item.value}>{item.label}</option>
              ))}
            </select>
          </label>
        </div>

        <div className="archive-actions">
          <button className="primary-btn" onClick={() => startArchive(false)}>
            Begin at the Door
          </button>
          <button className="secondary-btn" onClick={() => startArchive(true)}>
            Knock
          </button>
        </div>

        {error && (
          <p style={{ color: 'var(--danger)', marginTop: '1rem', fontSize: '0.9rem' }}>
            {error}
          </p>
        )}

        <p className="small-text">
          Emotions and themes are not entered by the user. They are inferred by the analysis layer.
        </p>
      </div>
    </section>
  );
}
