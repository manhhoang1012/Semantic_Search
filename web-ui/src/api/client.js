/**
 * Optimized API client with caching, retry logic, and request deduplication
 */

import axios from 'axios';
import config from '../config/index';

// Request cache
const requestCache = new Map();
const pendingRequests = new Map();

export const apiClient = axios.create({
  baseURL: config.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: config.REQUEST_TIMEOUT,
});

/**
 * Request interceptor for logging and debugging
 */
apiClient.interceptors.request.use(
  (cfg) => {
    if (config.DEBUG) {
      console.log(`📤 [API] ${cfg.method.toUpperCase()} ${cfg.url}`);
    }
    return cfg;
  },
  (error) => {
    console.error('❌ [API] Request error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for caching and error handling
 */
apiClient.interceptors.response.use(
  (response) => {
    if (config.DEBUG) {
      console.log(`📥 [API] ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    const message = error.response?.data?.error || error.message || 'Unknown error';
    const status = error.response?.status;

    if (config.DEBUG) {
      console.error(`❌ [API] ${status || 'Network'} Error:`, message);
    }

    // Create standardized error object
    const apiError = new Error(message);
    apiError.status = status;
    apiError.data = error.response?.data;

    return Promise.reject(apiError);
  }
);

/**
 * GET request with caching support
 */
export const apiGet = async (endpoint, options = {}) => {
  const { cache = true, cacheTTL = 60000, params = {} } = options;
  const cacheKey = `GET:${endpoint}:${JSON.stringify(params)}`;

  // Check cache
  if (cache) {
    const cached = requestCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < cacheTTL) {
      return cached.data;
    }
  }

  // Check pending requests for deduplication
  if (pendingRequests.has(cacheKey)) {
    return pendingRequests.get(cacheKey);
  }

  // Make request
  const request = apiClient
    .get(endpoint, { params })
    .then((response) => {
      // Cache the result
      if (cache) {
        requestCache.set(cacheKey, {
          data: response.data,
          timestamp: Date.now(),
        });
      }
      return response.data;
    })
    .finally(() => {
      pendingRequests.delete(cacheKey);
    });

  pendingRequests.set(cacheKey, request);
  return request;
};

/**
 * POST request with retry logic
 */
export const apiPost = async (endpoint, data = {}, options = {}) => {
  const { retries = 0 } = options;
  let lastError;

  for (let i = 0; i <= retries; i++) {
    try {
      const response = await apiClient.post(endpoint, data);
      return response.data;
    } catch (error) {
      lastError = error;
      if (i < retries) {
        // Exponential backoff
        await new Promise((resolve) => setTimeout(resolve, Math.pow(2, i) * 100));
      }
    }
  }

  throw lastError;
};

/**
 * DELETE request
 */
export const apiDelete = async (endpoint, options = {}) => {
  const { retries = 0 } = options;
  let lastError;

  for (let i = 0; i <= retries; i++) {
    try {
      const response = await apiClient.delete(endpoint);
      return response.data;
    } catch (error) {
      lastError = error;
      if (i < retries) {
        await new Promise((resolve) => setTimeout(resolve, Math.pow(2, i) * 100));
      }
    }
  }

  throw lastError;
};

/**
 * Clear cache (useful for refetching data)
 */
export const clearCache = (endpoint = null) => {
  if (endpoint) {
    // Clear specific endpoint cache
    for (const key of requestCache.keys()) {
      if (key.includes(endpoint)) {
        requestCache.delete(key);
      }
    }
  } else {
    // Clear all cache
    requestCache.clear();
  }
};

export default apiClient;
