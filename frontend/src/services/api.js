import axios from 'axios';

// Use /api in production (nginx proxy), localhost in development
const API_BASE_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

export const chatAPI = {
  // Send a chat message
  sendMessage: async (message, sessionId = null) => {
    const response = await api.post('/chat', {
      message,
      session_id: sessionId,
    });
    return response.data;
  },

  // Upload a PDF file
  uploadPDF: async (file, sessionId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await api.post('/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get session history
  getHistory: async (sessionId) => {
    const response = await api.get(`/session/${sessionId}/history`);
    return response.data;
  },

  // Delete session
  deleteSession: async (sessionId) => {
    const response = await api.delete(`/session/${sessionId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
