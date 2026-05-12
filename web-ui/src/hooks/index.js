/**
 * Custom hooks for state management and API calls
 * Reusable logic across components
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { apiGet, apiPost, apiDelete, clearCache } from '../api/client';
import config from '../config/index';

/**
 * useDebounce - Debounce value changes
 */
export const useDebounce = (value, delay = 300) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

/**
 * useAsync - Handle async operations with loading/error states
 */
export const useAsync = (asyncFunction, immediate = true) => {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  // Use useRef to track if component is mounted
  const isMountedRef = useRef(true);

  const execute = useCallback(
    async (...args) => {
      setStatus('pending');
      setData(null);
      setError(null);

      try {
        const response = await asyncFunction(...args);
        if (isMountedRef.current) {
          setData(response);
          setStatus('success');
        }
        return response;
      } catch (err) {
        if (isMountedRef.current) {
          setError(err);
          setStatus('error');
        }
        throw err;
      }
    },
    [asyncFunction]
  );

  useEffect(() => {
    if (immediate) {
      execute();
    }

    return () => {
      isMountedRef.current = false;
    };
  }, [execute, immediate]);

  return { execute, status, data, error, isLoading: status === 'pending' };
};

/**
 * useSearch - Handle search operations with debouncing
 */
export const useSearch = (initialTopK = config.SEARCH.DEFAULT_TOP_K) => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(initialTopK);
  const [results, setResults] = useState([]);
  const [latency, setLatency] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const debouncedQuery = useDebounce(query, config.SEARCH.DEBOUNCE_MS);

  const search = useCallback(
    async (searchQuery, topKValue = topK) => {
      if (!searchQuery.trim()) {
        setResults([]);
        return;
      }

      setLoading(true);
      setError('');

      try {
        const data = await apiPost(config.ENDPOINTS.SEARCH, {
          query: searchQuery,
          top_k: topKValue,
        });

        if (data && data.results) {
          setResults(data.results);
          setLatency(data.latency_ms || 0);
        }
      } catch (err) {
        setError(err.message || 'Failed to fetch results');
        setResults([]);
      } finally {
        setLoading(false);
      }
    },
    [topK]
  );

  return {
    query,
    setQuery,
    topK,
    setTopK,
    results,
    setResults,
    latency,
    loading,
    error,
    search,
    debouncedQuery,
  };
};

/**
 * usePagination - Handle pagination logic
 */
export const usePagination = (items, pageSize = config.PAGINATION.DEFAULT_PAGE_SIZE) => {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(items.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentItems = items.slice(startIndex, endIndex);

  const goToPage = useCallback((page) => {
    const pageNumber = Math.max(1, Math.min(page, totalPages || 1));
    setCurrentPage(pageNumber);
  }, [totalPages]);

  const nextPage = useCallback(() => goToPage(currentPage + 1), [currentPage, goToPage]);
  const prevPage = useCallback(() => goToPage(currentPage - 1), [currentPage, goToPage]);

  return {
    currentPage,
    setCurrentPage: goToPage,
    totalPages,
    startIndex,
    endIndex,
    currentItems,
    nextPage,
    prevPage,
    hasPreviousPage: currentPage > 1,
    hasNextPage: currentPage < totalPages,
  };
};

/**
 * useFetch - Fetch data with caching and refetch capability
 */
export const useFetch = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiGet(endpoint, options);
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, [endpoint, options]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const refetch = useCallback(() => {
    clearCache(endpoint);
    return fetch();
  }, [endpoint, fetch]);

  return { data, loading, error, refetch };
};

/**
 * useLocalStorage - Persist state to localStorage
 */
export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.error(error);
      }
    },
    [key, storedValue]
  );

  return [storedValue, setValue];
};
