/**
 * ConversationPanel — The Echoing Threshold
 * The chat interface: user input + character responses with typewriter effect.
 */
import { useState, useEffect, useRef } from 'react';

const SENTIMENT_LABELS = {
  melancholy: { label: '◆ melancholy', color: '#4a7fa5' },
  resistance: { label: '◆ resistance', color: '#c0392b' },
  hope: { label: '◆ hope', color: '#d4a044' },
  neutral: { label: '◆ drifting', color: '#888' },
};

function TypewriterText({ text, speed = 28 }) {
  const [displayed, setDisplayed] = useState('');
  const indexRef = useRef(0);
  const timerRef = useRef(null);

  useEffect(() => {
    setDisplayed('');
    indexRef.current = 0;
    clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      if (indexRef.current >= text.length) {
        clearInterval(timerRef.current);
        return;
      }
      setDisplayed(text.slice(0, indexRef.current + 1));
      indexRef.current++;
    }, speed);
    return () => clearInterval(timerRef.current);
  }, [text, speed]);

  return <span>{displayed}<span className="cursor-blink">|</span></span>;
}

export default function ConversationPanel({
  messages,
  isTyping,
  onSend,
  lastEmotion,
  turnCount,
}) {
  const [input, setInput] = useState('');
  const [lastRenderedId, setLastRenderedId] = useState(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    setInput('');
    onSend(text);
    inputRef.current?.focus();
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const sentiment = lastEmotion?.sentiment;
  const sentInfo = SENTIMENT_LABELS[sentiment] || SENTIMENT_LABELS.neutral;
  const intensity = lastEmotion?.intensity ?? 0;

  return (
    <div className="conversation-panel">
      {/* Header */}
      <div className="conv-header">
        <div className="conv-title">
          <span className="conv-char-name">Bob Dylan</span>
          <span className="conv-char-year">• 1973</span>
        </div>
        {lastEmotion && (
          <div className="conv-emotion-badge" style={{ color: sentInfo.color }}>
            {sentInfo.label}
            <div className="intensity-bar">
              <div
                className="intensity-fill"
                style={{
                  width: `${intensity * 100}%`,
                  background: sentInfo.color,
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="conv-messages">
        {messages.map((msg, i) => {
          const isLatestChar = msg.role === 'character' && i === messages.length - 1;
          return (
            <div key={msg.id} className={`conv-message ${msg.role}`}>
              {msg.role === 'character' && (
                <div className="char-avatar">
                  <span>BD</span>
                </div>
              )}
              <div className="msg-bubble">
                {isLatestChar ? (
                  <TypewriterText text={msg.content} speed={22} />
                ) : (
                  <span>{msg.content}</span>
                )}
                {msg.emotion?.theme_match && (
                  <span className="msg-theme">— {msg.emotion.theme_match}</span>
                )}
              </div>
            </div>
          );
        })}

        {isTyping && (
          <div className="conv-message character typing">
            <div className="char-avatar"><span>BD</span></div>
            <div className="msg-bubble typing-indicator">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="conv-input-area">
        <textarea
          ref={inputRef}
          className="conv-input"
          placeholder="Speak your truth..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          rows={2}
          disabled={isTyping}
        />
        <button
          className="conv-send-btn"
          onClick={handleSend}
          disabled={isTyping || !input.trim()}
        >
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>

      {turnCount > 0 && (
        <div className="conv-turn-count">
          {turnCount} exchange{turnCount !== 1 ? 's' : ''} at the threshold
        </div>
      )}
    </div>
  );
}
