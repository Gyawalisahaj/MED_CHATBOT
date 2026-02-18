/**
 * API Client for Medical RAG Chatbot
 * Handles all communication with the backend REST API
 */

import axios from 'axios';

class MedicalChatAPIClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add error interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  /**
   * Send a medical query to the RAG pipeline
   * @param {string} message - Medical question
   * @param {string} sessionId - User session identifier
   * @returns {Promise<{answer: string, sources: string[], session_id: string}>}
   */
  async sendMessage(message, sessionId = 'default_session') {
    try {
      const response = await this.axiosInstance.post('/api/v1/chat/query', {
        message,
        session_id: sessionId,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to send message: ${error.message}`);
    }
  }

  /**
   * Retrieve chat history for a session
   * @param {string} sessionId - User session identifier
   * @returns {Promise<Array>} Array of chat history items
   */
  async getChatHistory(sessionId) {
    try {
      const response = await this.axiosInstance.get(
        `/api/v1/chat/history/${sessionId}`
      );
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return []; // No history found
      }
      throw new Error(`Failed to fetch chat history: ${error.message}`);
    }
  }

  /**
   * Clear chat history for a session
   * @param {string} sessionId - User session identifier
   * @returns {Promise<{message: string}>}
   */
  async clearChatHistory(sessionId) {
    try {
      const response = await this.axiosInstance.delete(
        `/api/v1/chat/history/${sessionId}`
      );
      return response.data;
    } catch (error) {
      throw new Error(`Failed to clear chat history: ${error.message}`);
    }
  }

  /**
   * Check if backend is healthy
   * @returns {Promise<{status: string, service: string}>}
   */
  async healthCheck() {
    try {
      const response = await this.axiosInstance.get('/api/v1/chat/health');
      return response.data;
    } catch (error) {
      throw new Error(`Health check failed: ${error.message}`);
    }
  }

  /**
   * Perform advanced medical search with structured filters
   * @param {object} searchParams - Search parameters
   * @returns {Promise<object>} Advanced search response
   */
  async advancedSearch(searchParams) {
    try {
      const response = await this.axiosInstance.post(
        '/api/v1/chat/advanced-search',
        searchParams
      );
      return response.data;
    } catch (error) {
      throw new Error(`Advanced search failed: ${error.message}`);
    }
  }

  /**
   * Get document metadata
   * @returns {Promise<Array>} List of ingested documents
   */
  async getDocuments() {
    try {
      const response = await this.axiosInstance.get(
        '/api/v1/chat/documents'
      );
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch documents: ${error.message}`);
    }
  }
}

export default MedicalChatAPIClient;
