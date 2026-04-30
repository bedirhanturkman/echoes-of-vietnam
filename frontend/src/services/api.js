/**
 * API Service — The Echoing Threshold
 * Communicates with the FastAPI backend conversation pipeline.
 */

const BASE_URL = 'http://localhost:8000/api/v1';

export const api = {
  /**
   * Start a new conversation session with a character.
   * @param {string} character - e.g. "bob_dylan_1973"
   * @returns {Promise<StartSessionResponse>}
   */
  async startSession(character = 'bob_dylan_1973') {
    const res = await fetch(`${BASE_URL}/conversation/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ character }),
    });
    if (!res.ok) throw new Error(`Start session failed: ${res.status}`);
    return res.json();
  },

  /**
   * Send a message and receive full ThresholdResponse.
   * @param {string} sessionId
   * @param {string} message
   * @param {string} character
   * @returns {Promise<ThresholdResponse>}
   */
  async sendMessage(sessionId, message, character = 'bob_dylan_1973') {
    const res = await fetch(`${BASE_URL}/conversation/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        message,
        character,
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
