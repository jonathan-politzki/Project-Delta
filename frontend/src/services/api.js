// frontend/src/services/api.js

import axios from 'axios';

const API_URL = 'https://project-delta-app-6f4ac4c9390d.herokuapp.com';

export const analyzeUrl = async (url) => {
  try {
    console.log('Sending request to:', `${API_URL}/api/v1/analysis/`);
    const response = await axios.post(`${API_URL}/api/v1/analysis/`, { url });
    console.log('Received response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in analyzeUrl:', error);
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Error status:', error.response.status);
      console.error('Error headers:', error.response.headers);
    }
    throw error;
  }
};