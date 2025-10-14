// frontend/src/api/coreApi.js
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


export const getProjects = async () => {
  try {
    console.log("Fetching projects...");
    const response = await api.get('projects/');
    console.log("Projects fetched:", response.data);
    return response.data;
    } catch (error) {
    console.error('Fetch projects error:', error.response ? error.response.data : error.message);
    throw error;  
  }
};

export const getUsers = async () => {
    try{
        const response = await api.get('users/');
        return response.data;
    }
    catch (error) {
        let errorMessage = 'Unknown error';
        if (error.response && error.response.data) {
            errorMessage = JSON.stringify(error.response.data);
        }
        throw new Error(errorMessage);
    }
};
