/**
 * App.jsx - The Echoing Threshold application shell.
 */
import './App.css';
import { useConversation } from './hooks/useConversation';
import AtmosphereCanvas from './components/AtmosphereCanvas';
import ThresholdDoor from './components/ThresholdDoor';
import ConversationPanel from './components/ConversationPanel';
import HistoricalContext from './components/HistoricalContext';
import AudioEngine from './components/AudioEngine';

export default function App() {
  const {
    phase,
    messages,
    isTyping,
    error,
    visualParams,
    musicParams,
    historicalNote,
    turnCount,
    lastEmotion,
    currentCharacter,
    startSession,
    sendMessage,
    resetSession,
  } = useConversation();

  return (
    <div className={`app-root palette-${visualParams.color_palette}`}>
      <AtmosphereCanvas visualParams={visualParams} />

      <div className="app-ui">
        {(phase === 'intro' || phase === 'loading') && (
          <div className="intro-screen">
            <header className="intro-header">
              <h1 className="intro-title">The Echoing Threshold</h1>
              <p className="intro-subtitle">
                A conversation that summons the voice it needs
              </p>
              <p className="intro-tagline">
                "Every man has a door he keeps half-open, half-closed."
              </p>
            </header>

            <div className="door-stage">
              <ThresholdDoor
                doorState="closed"
                colorPalette={visualParams.color_palette}
                intensity={0.4}
                isIntro={true}
                onKnock={startSession}
                isLoading={phase === 'loading'}
              />
            </div>

            <div className="intro-context">
              <p>Paris Peace Accords signed. The war is ending.</p>
              <p>Dylan is scoring a western about outlaws and fatalism.</p>
              <p>He writes <em>Knockin' on Heaven's Door.</em></p>
              <p>The door is waiting.</p>
            </div>

            {error && <div className="error-banner">{error}</div>}
          </div>
        )}

        {phase === 'conversation' && (
          <div className="conversation-screen">
            <div className="door-sidebar">
              <ThresholdDoor
                doorState={visualParams.door_state}
                colorPalette={visualParams.color_palette}
                intensity={lastEmotion?.intensity ?? 0.5}
                isIntro={false}
              />
              <button className="leave-btn" onClick={resetSession} title="Walk away">
                leave
              </button>
            </div>

            <main className="conv-main">
              <ConversationPanel
                messages={messages}
                isTyping={isTyping}
                onSend={sendMessage}
                lastEmotion={lastEmotion}
                turnCount={turnCount}
                currentCharacter={currentCharacter}
              />
            </main>

            <HistoricalContext
              note={historicalNote}
              musicParams={musicParams}
            />

            {error && <div className="error-banner floating">{error}</div>}
          </div>
        )}
      </div>

      <AudioEngine musicParams={musicParams} />
    </div>
  );
}
