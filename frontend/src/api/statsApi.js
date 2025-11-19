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


export const getDashboardStats = async () => {
    try {
        const response = await api.get('stats/dashboard/')
        return response.data
    } catch (error) {
        console.error('Error fetching dashboard stats:', error)
        throw error
    }
}
 
export const getReportsOverview = async () => {
  try {
    const response = await api.get('stats/reports/overview/')
    return response.data
  } catch (error) {
    console.error('Error fetching reports overview:', error)
    throw error
  }
}

  export const getReportsMembersWorkload = async () => {
    try {
      const response = await api.get('stats/reports/members-workload/')
      return response.data
    } catch (error) {
      console.error('Error fetching members workload:', error)
      throw error
    }
  }