import { useState } from 'react';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';
import { apiClient } from './api/client';

function App() {
  const [results, setResults] = useState([]);
  const [latency, setLatency] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [topK, setTopK] = useState(5);

  const handleSearch = async (query) => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    
    try {
      const res = await apiClient.post('/search', { query, top_k: topK });
      setResults(res.data.results || []);
      setLatency(res.data.latency);
    } catch (err) {
      setError('Failed to fetch results from the server.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <div className="text-center mb-10">
        <h1 className="text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
          Semantic Knowledge Base
        </h1>
        <p className="text-gray-400">Search through the vector database using natural language.</p>
      </div>

      <SearchBar onSearch={handleSearch} loading={loading} topK={topK} setTopK={setTopK} />

      {error && <div className="text-red-400 mt-4 text-center">{error}</div>}

      <div className="mt-8">
        {latency && (
          <div className="text-sm text-gray-500 mb-4 text-right">
            Response time: {(latency * 1000).toFixed(2)} ms
          </div>
        )}
        
        <div className="flex flex-col gap-4">
          {results.map((item, idx) => (
            <ResultCard key={item.id || idx} item={item} />
          ))}
          {!loading && results.length === 0 && latency !== null && (
            <div className="text-center text-gray-500 mt-8">No relevant results found.</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
