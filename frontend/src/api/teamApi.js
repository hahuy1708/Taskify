// frontend/src/api/teamApi.js
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

export const getListTeams = async () => {
  try{
    const response = await api.get('teams/');
    console.log("Teams fetched:", response.data);
    return response.data;
  }catch(error){
    console.error('Fetch error:', error.response ? error.response.data : error.message);
    throw error;  
  }
}

export const getTeamMembers = async (id) => {
  try {
    const response = await api.get(`teams/${id}/members`);
    console.log("Team members fetched:", response.data);
    return response.data;
    } catch (error) {
    console.error('Fetch error:', error.response ? error.response.data : error.message);
    throw error;  
  }
};


export const addMembersToTeam = async (teamId, membersArray) => {
  try {
    const response = await api.post(`teams/${teamId}/members/add`, membersArray);
    console.log('Add members response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Add members error:', error.response ? error.response.data : error.message);
    throw error;
  }
};
