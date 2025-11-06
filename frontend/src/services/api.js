import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'https://singaji-setu-agent-production.up.railway.app'
    : 'http://localhost:8080',
  headers: {
    'Content-Type': 'application/json',
  }
});

export default api;
