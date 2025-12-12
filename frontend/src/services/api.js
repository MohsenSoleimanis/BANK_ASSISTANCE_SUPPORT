import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

export const chatAPI = {
  sendMessage: async (message, sessionId = null) => {
    try {
      const response = await api.post('/chat/', {
        message,
        session_id: sessionId,
        context: {},
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error.response?.data || error.message);
      throw error;
    }
  },

  getHealth: async () => {
    const response = await api.get('/health/');
    return response.data;
  },
};

export default api;