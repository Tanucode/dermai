/**
 * services/api.js
 * ----------------
 * This file handles ALL communication between React and FastAPI.
 * 
 * CONCEPT — Axios:
 *   Axios is an HTTP client (like fetch, but better).
 *   It makes API calls: GET, POST, PUT, DELETE
 *   It automatically handles JSON parsing, errors, and headers.
 * 
 * CONCEPT — API Layer Pattern:
 *   Instead of making fetch() calls in every component,
 *   we centralize ALL API calls here.
 *   This makes it easy to:
 *   - Change the backend URL in ONE place
 *   - Add auth headers globally
 *   - Handle errors consistently
 */

import axios from 'axios';

// Base URL for our FastAPI backend
// In development: Vite proxy handles this (see vite.config.js)
// In production (Vercel): Set VITE_API_URL to your Render backend URL
const API_BASE = import.meta.env.VITE_API_URL || '/api';

// Create an axios instance with default settings
const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes — AI analysis takes time!
});

// ── Interceptor: auto-add auth token to every request ─────────────────
// CONCEPT — Interceptors:
//   Code that runs BEFORE every request or AFTER every response.
//   We use it to automatically attach the JWT token.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('dermai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── ANALYSIS ENDPOINTS ────────────────────────────────────────────────

/**
 * Upload an image and get skin analysis.
 * 
 * CONCEPT — FormData:
 *   When uploading files, you can't send JSON.
 *   You use FormData — a browser API for multipart/form-data.
 *   FastAPI receives this as UploadFile.
 */
export const analyzeSkin = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

/**
 * Get a specific analysis by its ID.
 */
export const getAnalysis = async (analysisId) => {
  const response = await api.get(`/analyze/${analysisId}`);
  return response.data;
};

// ── HISTORY ENDPOINTS ─────────────────────────────────────────────────

/**
 * Get recent analysis history.
 */
export const getHistory = async (limit = 10) => {
  const response = await api.get(`/history/?limit=${limit}`);
  return response.data;
};

/**
 * Get one full analysis from history.
 */
export const getHistoryItem = async (analysisId) => {
  const response = await api.get(`/history/${analysisId}`);
  return response.data;
};

/**
 * Delete a saved analysis.
 */
export const deleteAnalysis = async (analysisId) => {
  const response = await api.delete(`/history/${analysisId}`);
  return response.data;
};

// ── AUTH ENDPOINTS ────────────────────────────────────────────────────

export const registerUser = async (name, email, password) => {
  const response = await api.post('/auth/register', { name, email, password });
  // Save token to localStorage
  localStorage.setItem('dermai_token', response.data.access_token);
  return response.data;
};

export const loginUser = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  localStorage.setItem('dermai_token', response.data.access_token);
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const logoutUser = () => {
  localStorage.removeItem('dermai_token');
};

export default api;
