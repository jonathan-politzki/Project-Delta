// frontend/src/services/api.js

const API_URL = 'http://localhost:8000/api/v1';

export const analyzeUrl = async (url) => {
  try {
    const response = await fetch(`${API_URL}/analysis/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};