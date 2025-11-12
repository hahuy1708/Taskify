// frontend/src/api/comment_checklistApi.js
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
// Comment APIs
export const getComments = async (taskId) => {
  try {
    const response = await api.get(`tasks/${taskId}/comments/`);
    return response.data;
  } catch (error) {
    console.error('Fetch comments error:', error.response ? error.response.data : error.message);
    throw error;
  }
};

export const updateComment = async (id, data) => {
  const response = await api.patch(`comments/update/${id}/`, data)
  return response.data
}

export const createComment = async (taskId, data) => {
  const response = await api.post(`tasks/${taskId}/comments/create/`, data)
  return response.data
}

export const deleteComment = async (id) => {
  try {
    await api.delete(`comments/delete/${id}/`);
  } catch (error) {
    console.error('Delete comment error:', error.response ? error.response.data : error.message);
    throw error;
  }
};

// Checklist APIs
export const getChecklistItems = async (taskId) => {
  try {
    const response = await api.get(`tasks/${taskId}/checklist/`)
    return response.data
  } catch (error) {
    console.error('Fetch checklist items error:', error.response ? error.response.data : error.message)
    throw error
  }
}

export const createChecklistItem = async (taskId, data) => {
  try {
    const response = await api.post(`tasks/${taskId}/checklist/create/`, data)
    return response.data
  } catch (error) {
    console.error('Create checklist item error:', error.response ? error.response.data : error.message)
    throw error
  }
}

export const updateChecklistItem = async (itemId, data) => {
  try {
    const response = await api.patch(`checklist/${itemId}/update/`, data)
    return response.data
  } catch (error) {
    console.error('Update checklist item error:', error.response ? error.response.data : error.message)
    throw error
  }
}

export const deleteChecklistItem = async (itemId) => {
  try {
    await api.delete(`checklist/${itemId}/delete/`)
  } catch (error) {
    console.error('Delete checklist item error:', error.response ? error.response.data : error.message)
    throw error
  }
}