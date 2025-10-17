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

export const updateProject = async (id, data, role) => {
  // Only send allowed fields based on role
  const allowedFields = role === 'admin' 
    ? ['name', 'description', 'deadline', 'owner', 'leader', 'is_personal', 'is_completed']
    : ['description', 'is_completed']
  
  const filteredData = Object.keys(data)
    .filter(key => allowedFields.includes(key))
    .reduce((obj, key) => ({ ...obj, [key]: data[key] }), {})

  const response = await api.patch(`projects/${id}/`, filteredData)
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
  await api.delete(`projects/${id}/`)
}

export const createProject = async (data) => {
  const response = await api.post('projects/', data)
  return response.data
}