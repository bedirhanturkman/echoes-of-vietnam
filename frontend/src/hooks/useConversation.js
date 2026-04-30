/**
 * useConversation — The Echoing Threshold
 * Core hook managing session state, message flow, and atmospheric params.
 */
import { useState, useCallback, useRef } from 'react';
import { api } from '../services/api';

const INITIAL_VISUAL = {
  color_palette: 'blue_grey',
  cloud_density: 0.4,
  door_state: 'closed',
  particle_intensity: 0.1,
};

const INITIAL_MUSIC = {
  tempo_bpm: 72,
  key: 'G',
  instrument_layer: 'ambient_only',
  rhythm_type: 'steady',
  chord_progression_type: 'neutral',
  reverb_intensity: 0.6,
  historical_soundscape: 'radio_static',
  cross_fade_seconds: 3.0,
};

export function useConversation() {
  const [phase, setPhase] = useState('intro'); // intro | loading | conversation
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [visualParams, setVisualParams] = useState(INITIAL_VISUAL);
  const [musicParams, setMusicParams] = useState(INITIAL_MUSIC);
  const [historicalNote, setHistoricalNote] = useState(null);
  const [turnCount, setTurnCount] = useState(0);
  const [lastEmotion, setLastEmotion] = useState(null);
  const character = 'bob_dylan_1973';
  const abortRef = useRef(null);

  /**
   * Initialize session — user knocked on the door.
   */
  const startSession = useCallback(async () => {
    setPhase('loading');
    setError(null);
    try {
      const data = await api.startSession(character);
      setSessionId(data.session_id);
      setVisualParams(data.initial_visual);
      setMusicParams(data.initial_music);

      // Add Dylan's greeting as first message
      setMessages([
        {
          id: 'greeting',
          role: 'character',
          content: data.greeting,
          emotion: null,
          timestamp: Date.now(),
        },
      ]);
      setPhase('conversation');
    } catch (err) {
      setError('Could not reach the threshold. Is the server running?');
      setPhase('intro');
    }
  }, [character]);

  /**
   * Send user message through the pipeline.
   */
  const sendMessage = useCallback(
    async (userText) => {
      if (!sessionId || isTyping || !userText.trim()) return;

      const userMsg = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: userText.trim(),
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setIsTyping(true);
      setError(null);

      try {
        const data = await api.sendMessage(sessionId, userText, character);

        // Update atmosphere
        setVisualParams(data.visual_params);
        setMusicParams(data.music_params);
        setHistoricalNote(data.historical_note);
        setTurnCount(data.turn_count);
        setLastEmotion(data.emotion);

        // Add character response
        const charMsg = {
          id: `char-${Date.now()}`,
          role: 'character',
          content: data.emotion.character_response,
          emotion: data.emotion,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, charMsg]);
      } catch (err) {
        setError('The signal was lost... try again.');
      } finally {
        setIsTyping(false);
      }
    },
    [sessionId, isTyping, character]
  );

  /**
   * Reset everything — walk away from the door.
   */
  const resetSession = useCallback(() => {
    setPhase('intro');
    setSessionId(null);
    setMessages([]);
    setIsTyping(false);
    setError(null);
    setVisualParams(INITIAL_VISUAL);
    setMusicParams(INITIAL_MUSIC);
    setHistoricalNote(null);
    setTurnCount(0);
    setLastEmotion(null);
  }, []);

  return {
    phase,
    sessionId,
    messages,
    isTyping,
    error,
    visualParams,
    musicParams,
    historicalNote,
    turnCount,
    lastEmotion,
    startSession,
    sendMessage,
    resetSession,
  };
}
