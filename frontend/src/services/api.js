// frontend/src/services/api.js

import axios from 'axios';

const HEROKU_URL = 'https://project-delta-app-6f4ac4c9390d.herokuapp.com';
let API_URL = HEROKU_URL;

const getConfig = async () => {
  try {
    const response = await axios.get(`${HEROKU_URL}/api/config`);
    API_URL = response.data.apiUrl;
  } catch (error) {
    console.error('Failed to fetch config:', error);
    // Fallback to the Heroku URL if config fetch fails
    API_URL = HEROKU_URL;
  }
};

export const analyzeUrl = async (url) => {
  try {
    await getConfig();
    const response = await axios.post(`${API_URL}/api/v1/analysis/`, { url });
    return response.data;
  } catch (error) {
    console.error('Error in analyzeUrl:', error);
    throw error;
  }
};