// frontend/src/api/userApi.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/core/',  
  headers: { 'Content-Type': 'application/json' },
});


api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
    if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});  

export const getUsers = async () => {
    try{
        const response = await api.get('users/members/')
        return response.data;
    } catch (error) {
        console.error('Error fetching users:', error);
        throw error;
    }
}

export const getLeaders = async () => {
    try{
        const response = await api.get('users/leaders/')
        return response.data;
    }
    catch (error) {
        console.error('Error fetching leaders:', error);
        throw error;
    }
}
