// frontend/src/services/api.js

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://project-delta-app-6f4ac4c9390d.herokuapp.com';

// const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: false,
});

export const analyzeUrl = async (url) => {
  try {
    console.log('Sending analysis request for URL:', url);
    const response = await api.post('/api/v1/analysis/', { url });
    console.log('Received analysis response:', response.data);
    
    if (!response.data || !response.data.task_id) {
      throw new Error('Invalid response from server');
    }
    
    return response.data;
  } catch (error) {
    console.error('Error in analyzeUrl:', error.response?.data || error.message);
    throw error.response?.data || error;
  }
};

export const getAnalysisStatus = async (taskId) => {
  try {
    console.log('Checking status for task:', taskId);
    const response = await api.get(`/api/v1/analysis/status/${taskId}`);
    console.log('Received status update:', response.data);
    
    if (!response.data || !response.data.status) {
      throw new Error('Invalid status response from server');
    }
    
    if (response.data.status === 'completed') {
      console.log('Parsed analysis result:', JSON.stringify(response.data.result, null, 2));
    }
    
    return response.data;
  } catch (error) {
    console.error('Error in getAnalysisStatus:', error.response?.data || error.message);
    throw error.response?.data || error;
  }
};