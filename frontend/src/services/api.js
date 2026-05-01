/**
 * API Service — The Echoing Threshold
 * Communicates with the FastAPI backend conversation pipeline.
 */

const BASE_URL = 'http://localhost:8000/api/v1';

export const api = {
  /**
   * Start a new adaptive conversation session.
   * @returns {Promise<StartSessionResponse>}
   */
  async startSession() {
    const res = await fetch(`${BASE_URL}/conversation/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!res.ok) throw new Error(`Start session failed: ${res.status}`);
    return res.json();
  },

  /**
   * Send a message and receive full ThresholdResponse.
   * @param {string} sessionId
   * @param {string} message
   * @param {string} selectedCharacter
   * @returns {Promise<ThresholdResponse>}
   */
  async sendMessage(sessionId, message, selectedCharacter = 'auto') {
    const res = await fetch(`${BASE_URL}/conversation/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        message,
        selected_character: selectedCharacter,
      }),
    });
    if (!res.ok) throw new Error(`Message failed: ${res.status}`);
    return res.json();
  },

  /**
   * Health check.
   * @returns {Promise<HealthResponse>}
   */
  async healthCheck() {
    const res = await fetch(`${BASE_URL}/health`);
    return res.json();
  },
};
