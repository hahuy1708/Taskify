// frontend/src/api/authApi.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/auth/',  
  headers: { 'Content-Type': 'application/json' },
});

const publicApi = axios.create({
  baseURL: 'http://localhost:8000/auth/',
  headers: { 'Content-Type': 'application/json' },
});


api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
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
      errorMessage = JSON.stringify(error.response.data);
    }
    console.error('Login failed:', error);
    throw new Error(errorMessage);  
  }
};

export const logout = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    await api.post('jwt/destroy/', { refresh: refreshToken });  
  }
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};


export const register = async (userData) => {
  try {
    const response = await publicApi.post('register/', userData);
    return response.data;
  } catch (error) {
    let errorMessage = 'Unknown error';
    if (error.response && error.response.data) {
      errorMessage = JSON.stringify(error.response.data);
    }
    console.error('Registration failed:', error);
    throw new Error(errorMessage);
  }
};

export const forgotPassword = async (data) => {
  try{
    const response = await publicApi.post('users/reset_password/', data); // email
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Request failed');
  }
}

export const resetPasswordConfirm = async (data) => {
  try{
    const response = await publicApi.post('users/reset_password_confirm/', data); // uuid, token
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Confirm failed');
  }
}

export const getProfile = async () => {
  const response = await api.get('users/me/');
  return response.data;
}

export const getUserDetail = async (userId) => {
    try {
        const response = await api.get(`users/${userId}/`);
        return response.data;
    } catch (error) {
        console.error('Error fetching user details:', error);
        throw error;
    }
}

export const updateProfile = async (data) => {
  try {
    const response = await api.patch('users/me/', data);
    return response.data;
  } catch (error) {
    let errorMessage = 'Unknown error';
    if (error.response && error.response.data) {
      errorMessage = JSON.stringify(error.response.data);
    }
    throw new Error(errorMessage);
  }
}

export const setPassword = async (data) => {
  try{
    const response = await api.post('users/set_password/', data); 
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Request failed');
  }
}

