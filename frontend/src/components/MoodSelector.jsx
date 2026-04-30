import { MOODS } from '../utils/musicGeneration';

export default function MoodSelector({ selectedMood, onMoodChange }) {
  return (
    <div className="mood-selector" aria-label="Mood selector">
      {Object.values(MOODS).map((mood) => (
        <button
          key={mood.id}
          type="button"
          className={`mood-option ${selectedMood === mood.id ? 'active' : ''}`}
          onClick={() => onMoodChange(mood.id)}
        >
          {mood.label}
        </button>
      ))}
    </div>
  );
}
