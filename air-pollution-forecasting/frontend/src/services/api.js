import axios from 'axios';
import toast from 'react-hot-toast';

// Base URL for your Flask API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('Making API request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server error
      toast.error(`Server Error: ${error.response.status}`);
    } else if (error.request) {
      // Network error
      toast.error('Network Error: Please check your connection');
    } else {
      // Other error
      toast.error('An unexpected error occurred');
    }
    return Promise.reject(error);
  }
);

export const fetchCurrentConditions = async (city) => {
  try {
    const response = await api.post('/api/current', { city });
    if (response.data.success) {
      toast.success(`Current conditions loaded for ${city}`);
      return response.data.conditions;
    } else {
      throw new Error(response.data.error || 'Failed to fetch current conditions');
    }
  } catch (error) {
    console.error('Error fetching current conditions:', error);
    throw error;
  }
};

export const fetchForecast = async (city, hours = 24) => {
  try {
    const response = await api.post('/api/forecast', { city, hours });
    if (response.data.success) {
      toast.success(`${hours}-hour forecast generated for ${city}`);
      return response.data;
    } else {
      throw new Error(response.data.error || 'Failed to fetch forecast');
    }
  } catch (error) {
    console.error('Error fetching forecast:', error);
    throw error;
  }
};

export const fetchHistoricalData = async (city, days = 7) => {
  try {
    const response = await api.post('/api/historical', { city, days });
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'Failed to fetch historical data');
    }
  } catch (error) {
    console.error('Error fetching historical data:', error);
    throw error;
  }
};

export const fetchCityList = async () => {
  try {
    const response = await api.get('/api/cities');
    if (response.data.success) {
      return response.data.cities;
    } else {
      throw new Error(response.data.error || 'Failed to fetch city list');
    }
  } catch (error) {
    console.error('Error fetching city list:', error);
    throw error;
  }
};

// Export the axios instance for custom requests
export default api;