// frontend/src/services/api.js

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://project-delta-app-6f4ac4c9390d.herokuapp.com';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: false,
});



export const analyzeUrl = async (url) => {
  try {
    const response = await api.post('/api/v1/analysis/', { url });
    return response.data;
  } catch (error) {
    console.error('Error in analyzeUrl:', error);
    throw error;
  }
};
