// frontend/src/api/projectApi.js
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


export const getProjects = async (search) => {
  try {
    const params = {};
    if (search) {
      params.search = search;
    }
    const response = await api.get('projects/', { params });
    return response.data;
    } catch (error) {
    console.error('Fetch projects error:', error.response ? error.response.data : error.message);
    throw error;  
  }
};

// export const getProjectDetails = async (projectId) => {
//   try {
//     console.log(`Fetching details for project ID: ${projectId}`);
//     const response = await api.get(`projects/${projectId}/kanban/`);
//     console.log("Project details fetched:", response.data);
//     return response.data;
//   } catch (error) {
//     console.error('Fetch project details error:', error.response ? error.response.data : error.message);
//     throw error;
//   }
// };

export const updateProject = async (id, data) => {
  // Let the backend serializer and permission rules decide what fields are allowed
  const response = await api.patch(`projects/update/${id}/`, data)
  return response.data
}

// export const getUsers = async () => {
//     try{
//         const response = await api.get('users/');
//         return response.data;
//     }
//     catch (error) {
//         let errorMessage = 'Unknown error';
//         if (error.response && error.response.data) {
//             errorMessage = JSON.stringify(error.response.data);
//         }
//         throw new Error(errorMessage);
//     }
// };

export const deleteProject = async (id) => {
  await api.delete(`projects/delete/${id}/`)
}

export const createProject = async (data) => {
  const response = await api.post('projects/create/', data)
  return response.data
}