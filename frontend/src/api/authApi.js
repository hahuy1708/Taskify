import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/auth/',  
  headers: { 'Content-Type': 'application/json' },
});

export const login = async (credentials) => {
  try {
    const response = await api.post('jwt/create/', credentials);
    // Lưu token vào localStorage hoặc Pinia store
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    return response.data;
  } catch (error) {
  let errorMessage = 'Unknown error';
    if (error.response && error.response.data) {
      errorMessage = JSON.stringify(error.response.data);  // Lấy detail từ backend (e.g., "No active account...")
    }
    console.error('Login failed:', error);
    throw new Error(errorMessage);  
  }
};