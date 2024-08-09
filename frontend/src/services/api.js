// frontend/src/services/api.js

import axios from 'axios';

let API_URL = 'http://localhost:8000'; // Default to localhost for development

const getConfig = async () => {
  try {
    // Replace this URL with your actual Heroku backend URL
    const response = await axios.get('https://project-delta-app-6f4ac4c9390d.herokuapp.com/api/config');
    API_URL = response.data.apiUrl;
  } catch (error) {
    console.error('Failed to fetch config:', error);
    // Fallback to the default URL if config fetch fails
  }
};

// Initialize the config
getConfig();

export const analyzeUrl = async (url) => {
  try {
    // Ensure config is fetched before making the request
    await getConfig();
    
    const response = await axios.post(`${API_URL}/api/v1/analysis/`, { url });
    return response.data;
  } catch (error) {
    console.error('Error in analyzeUrl:', error);
    throw error;
  }
};