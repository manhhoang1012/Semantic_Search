/**
 * Environment configuration
 * Centralized config for API endpoints and constants
 */

const ENV = {
  development: {
    API_BASE_URL: 'http://localhost:5000/api',
    DEBUG: true,
    REQUEST_TIMEOUT: 30000,
  },
  production: {
    API_BASE_URL: import.meta.env.VITE_API_URL || '/api',
    DEBUG: false,
    REQUEST_TIMEOUT: 30000,
  },
};

const currentEnv = import.meta.env.MODE === 'production' ? 'production' : 'development';

export const config = {
  ...ENV[currentEnv],
  // API Endpoints
  ENDPOINTS: {
    SEARCH: '/search/search',
    ADD: '/data/add',
    DELETE: '/data/delete',
    LIST: '/data/list',
    STATS: '/data/stats',
    HEALTH: '/health',
  },
  // Pagination
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 5,
    MAX_PAGE_SIZE: 100,
  },
  // Search
  SEARCH: {
    DEFAULT_TOP_K: 5,
    MIN_TOP_K: 1,
    MAX_TOP_K: 20,
    DEBOUNCE_MS: 300,
  },
  // Cache
  CACHE: {
    STATS_TTL: 30000, // 30s
    RESULTS_TTL: 60000, // 1min
  },
};

export default config;
