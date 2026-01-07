/**
 * Frontend Configuration
 * Centralizes environment-based configuration values
 */

// API URL Configuration
// In production, set REACT_APP_API_URL environment variable
// For example: REACT_APP_API_URL=https://api.yourdomain.com
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Other configuration values can be added here as needed
export const APP_NAME = 'Arbitrage OS';
export const APP_VERSION = '1.0.0';
